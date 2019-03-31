# Python Version: 3.x
import json

import config

import flask
import flask_cors
import mysql.connector
import onlinejudge


app = flask.Flask(__name__)
flask_cors.CORS(app)


def get_db():
    if 'db' not in flask.g:
        flask.g.db = mysql.connector.connect(
            host=config.MYSQL_HOST,
            port=config.MYSQL_PORT,
            user=config.MYSQL_USER,
            password=config.MYSQL_PASSWORD,
            database=config.MYSQL_DATABASE,
            charset='utf8mb4',
            sql_mode='TRADITIONAL,NO_AUTO_VALUE_ON_ZERO,ONLY_FULL_GROUP_BY',  # kamipo TRADITIONAL
            autocommit=True,
        )
    return flask.g.db

@app.teardown_appcontext
def teardown_db(exc):
    db = flask.g.pop('db', None)
    if db is not None:
        db.close()

@app.route("/")
def hello():
    return flask.jsonify({"message": "It works!"})

@app.route("/analyze", methods=["POST"])
def post_analyze():
    db = get_db()
    cur = db.cursor()

    # TODO: add CSRF tokens

    # restrict based on IP address
    cur.execute('SELECT 1 FROM jobs WHERE jobs.ip_address = INET6_ATON(%s)', (flask.request.remote_addr, ))
    if cur.fetchone() is not None:
        flask.abort(flask.make_response(flask.jsonify(message="You can make only one job in the queue at the same time. / 他の提出の処理が終わるまで待ってね"), 400))

    # parse URL
    submission = onlinejudge.dispatch.submission_from_url(flask.request.form['url'])
    if submission is None:
        flask.abort(flask.make_response(flask.jsonify(message="Your URL is unrecognized. / 提出ページの URL を入力してね"), 400))
    if not isinstance(submission, onlinejudge.service.atcoder.AtCoderSubmission):
        flask.abort(flask.make_response(flask.jsonify(message="Your URL is not supported. / まだ AtCoder だけだよ"), 400))

    # check whether duplicated or not
    cur.execute('''
        SELECT requests.id
            FROM submissions
            INNER JOIN requests ON submissions.id = requests.submission_id
        WHERE submissions.url = %s
    ''', (submission.get_url(), ))
    row = cur.fetchone()
    if row is not None:
        request_id, = row
        flask.abort(flask.make_response(flask.jsonify(message="Your URL have already been analyzed. / もう解析済みだったよ", id=request_id), 400))

    # get problem_id 
    problem = submission.get_problem()
    cur.execute('SELECT id FROM problems WHERE url = %s', (problem.get_url(), ))
    row = cur.fetchone()
    if row is not None:
        problem_id, = row
    else:
        contest = problem.get_contest()
        name = '{}: {}. {}'.format(contest.get_name(), problem.get_alphabet(), problem.get_name())
        samples = problem.download_sample_cases()
        db.start_transaction()
        cur.execute('INSERT INTO problems (url, name) VALUES (%s, %s)', (problem.get_url(), name))
        cur.execute('SELECT LAST_INSERT_ID()')
        problem_id, = cur.fetchone()
        for i, sample in enumerate(samples):
            cur.execute('INSERT INTO samples (problem_id, serial, input, output) VALUES (%s, %s, %s, %s)', (problem_id, i + 1, sample.input_data, sample.output_data or b''))
        db.commit()

    # get submission_id 
    url = submission.get_url()
    cur.execute('SELECT id FROM submissions WHERE url = %s', (submission.get_url(), ))
    row = cur.fetchone()
    if row is not None:
        submission_id, = row
    else:
        code = submission.download_code()
        user = submission.get_user_id()
        status = submission.get_status()
        language = submission.get_language_name()
        if 'C++' not in language:
            flask.abort(flask.make_response(flask.jsonify(message="The language must be a C++. / C++ での提出を指定してね", id=request_id), 400))
        if status not in ('WA', 'RE', 'TLE'):
            flask.abort(flask.make_response(flask.jsonify(message="The status of your submission must be WA, RE, or TLE. / WA か RE か TLE の提出を指定してね", id=request_id), 400))
        cur.execute('INSERT INTO submissions (problem_id, url, user, code, language, status) VALUES (%s, %s, %s, %s, %s, %s)', (problem_id, submission.get_url(), user, code, language, status))
        cur.execute('SELECT LAST_INSERT_ID()')
        submission_id, = cur.fetchone()

    # create a request
    db.start_transaction()
    cur.execute('INSERT INTO requests (submission_id) VALUES (%s)', (submission_id, ))
    cur.execute('SELECT LAST_INSERT_ID()')
    request_id, = cur.fetchone()
    cur.execute('INSERT INTO jobs (id, ip_address) VALUES (%s, INET6_ATON(%s))', (request_id, flask.request.remote_addr))
    db.commit()

    return flask.jsonify(message='OK', id=request_id)

@app.route("/result/<int:request_id>")
def get_result(request_id: int):
    cur = get_db().cursor(dictionary=True)
    cur.execute('''
        SELECT results.data, problems.name, submissions.user, submissions.status, submissions.url, submissions.code, submissions.language, results.created_at
            FROM results
            INNER JOIN requests ON results.id = requests.id
            INNER JOIN submissions ON requests.submission_id = submissions.id
            INNER JOIN problems ON submissions.problem_id = problems.id
        WHERE results.id = %s
    ''', (request_id, ))
    row = cur.fetchone()

    if row is None:
        cur.execute('SELECT 1 FROM jobs WHERE id = %s', (request_id, ))
        if cur.fetchone() is not None:
            return flask.abort(flask.make_response(flask.jsonify(message="Please wait...", id=request_id), 400))
        else:
            return flask.abort(flask.make_response(flask.jsonify(message="There is no such request."), 400))
    else:
        row['data'] = json.loads(row['data'])
        return flask.jsonify(row)

@app.route("/queue")
def get_queue():
    cur = get_db().cursor(dictionary=True)
    cur.execute('''
        SELECT requests.id, problems.name, submissions.user, submissions.status, requests.created_at, jobs.assigned_to
            FROM jobs
            INNER JOIN requests ON jobs.id = requests.id
            INNER JOIN submissions ON requests.submission_id = submissions.id
            INNER JOIN problems ON submissions.problem_id = problems.id
    ''')
    return flask.jsonify(cur.fetchall())

@app.route("/recent")
def get_results():
    cur = get_db().cursor(dictionary=True)
    cur.execute('''
        SELECT requests.id, problems.name, submissions.user, submissions.status, results.created_at
            FROM results
            INNER JOIN requests ON results.id = requests.id
            INNER JOIN submissions ON requests.submission_id = submissions.id
            INNER JOIN problems ON submissions.problem_id = problems.id
        ORDER BY results.created_at DESC
        LIMIT 10
    ''')
    return flask.jsonify(cur.fetchall())

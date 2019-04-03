# Python Version: 3.x
import json
import logging
import pathlib
import queue
import re
import sys
import tempfile
import threading
import time
import traceback

import config

import docker
import mysql.connector


def docker_exec(command, image=config.DOCKER_IMAGE, readonly=True, directory=None, timeout=None, client=None):
    client = client or docker.from_env()

    if directory is None:
        tempdir = tempfile.TemporaryDirectory()
        bind = tempdir.name
    else:
        bind = directory
    if readonly:
        mode = 'ro'
    else:
        mode = 'rw'
    working_dir = '/mnt/workspace'
    volumes = { bind: { 'bind': working_dir, 'mode': mode } }
    ulimits = []

    que = queue.Queue()
    try:
        container = client.containers.run(image, detach=True, stdin_open=True, volumes=volumes, working_dir=working_dir, ulimits=ulimits)
        try:
            def func():
                que.put(container.exec_run(command, demux=True))
            thread = threading.Thread(target=func)
            thread.start()
            thread.join(timeout=timeout)
        finally:
            container.kill()
    finally:
        if directory is None:
            tempdir.cleanup()
    return que.get()

def undertake_request(db):
    cur = db.cursor()
    try:
        db.start_transaction()
        cur.execute('''
            SELECT request_id
                FROM jobs
                INNER JOIN requests USING (request_id)
            WHERE jobs.assigned_to IS NULL
            ORDER BY requests.created_at
            FOR UPDATE
        ''')
        row = cur.fetchone()
        if row is None:
            request_id = None
        else:
            request_id, = row
            cur.execute('UPDATE jobs SET assigned_to = %s WHERE request_id = %s', (config.SERVER_NAME, request_id, ))
        db.commit()
    except mysql.connector.Error:
        traceback.print_exc()
        db.rollback()
        request_id = None
    if request_id is not None:
        logging.info('undertake request %d', request_id)
    return request_id

def run_compiler(compiler, options, code):
    assert compiler in ('g++', 'clang++')
    with tempfile.TemporaryDirectory() as tempdir:
        with open(pathlib.Path(tempdir) / 'main.cpp', 'w') as fh:
            fh.write(code)
        exit_code, (stdout, stderr) = docker_exec([compiler] + options + ['main.cpp'], directory=tempdir, readonly=False, timeout=10.0)
        if (pathlib.Path(tempdir) / 'a.out').exists():
            with open(pathlib.Path(tempdir) / 'a.out', 'rb') as fh:
                binary = fh.read()
        else:
            binary = None
    return exit_code, (stderr or b''), binary

def run_sample_test(binary, sample_input):
    with tempfile.TemporaryDirectory() as tempdir:
        with open(pathlib.Path(tempdir) / 'a.out', 'wb') as fh:
            fh.write(binary)
        (pathlib.Path(tempdir) / 'a.out').chmod(0o755)
        with open(pathlib.Path(tempdir) / 'sample.in', 'w') as fh:
            fh.write(sample_input)
        exit_code, (stdout, stderr) = docker_exec(['sh', '-c', 'valgrind ./a.out < sample.in'], directory=tempdir, timeout=3.0)
    return exit_code, (stdout or b''), (stderr or b'')

def serve_request(request_id, db):
    cur = db.cursor()

    # retrieve the data
    cur.execute('''
        SELECT problem_id, submissions.code
            FROM requests
            INNER JOIN submissions USING (submission_id)
            INNER JOIN problems USING (problem_id)
        WHERE request_id = %s
    ''', (request_id, ))
    problem_id, code = cur.fetchone()
    cur.execute('SELECT input, output FROM samples WHERE problem_id = %s ORDER BY serial', (problem_id, ))
    samples = cur.fetchall()

    # table
    compilers = ['g++', 'clang++']
    option_types = {
        'debug': ['-std=c++14', '-Wall', '-g3', '-fsanitize=undefined', '-D_GLIBCXX_DEBUG'],
        'optimized': ['-std=c++14', '-Wall', '-O3'],
    }

    # debug
    results = {}
    for compiler in compilers:
        for option_type, options in option_types.items():
            result = {}
            results['{}/{}'.format(compiler, option_type)] = result  # assign the reference
            result['compiler'] = compiler
            result['options'] = options

            # compile
            logging.info('compile with %s for %s', compiler, option_type)
            exit_code, stderr, binary = run_compiler(compiler, options, code)
            result['compiler_exit_code'] = exit_code
            result['compiler_stderr'] = stderr.decode()
            if exit_code != 0:
                continue

            # run with samples
            result['sample_results'] = []
            for i, (sample_input, sample_output) in enumerate(samples):
                logging.info('run sample %s', i + 1)
                exit_code, stdout, stderr = run_sample_test(binary, sample_input)
                result['sample_results'] += [{
                    'exit_code': exit_code,
                    'stdout': stdout.decode(),
                    'stderr': stderr.decode(),
                }]

    # summarize
    highlights = []
    checkboxes = []
    for compiler in compilers:
        for option_type, options in option_types.items():
            result = results['{}/{}'.format(compiler, option_type)]
            if result['compiler_exit_code']:
                continue
            for line in result['compiler_stderr'].splitlines():
                m = re.match(r'main\.cpp:(\d+):(\d+)', line)
                if m:
                    highlights += [{'level': 'warning', 'lineno': int(m.group(1))}]
            for result in result.get('sample_results'):
                for line in result['stderr'].splitlines():
                    m = re.match(r'main\.cpp:(\d+):(\d+)[: ]', line)
                    if m:
                        highlights += [{'level': 'error', 'lineno': int(m.group(1))}]
                        checkboxes += [line]
    highlights = list(map(dict, sorted(set(map(lambda x: tuple(sorted(x.items())), highlights)))))
    checkboxes = sorted(set(checkboxes))

    # write result
    data = {
        'version': 1,
        'id': request_id,
        'results': results,
        'highlights': highlights,
        'checkboxes': checkboxes,
    }
    cur.execute('INSERT INTO results (request_id, data) VALUES (%s, %s)', (request_id, json.dumps(data)))
    cur.execute('DELETE FROM jobs WHERE request_id = %s', (request_id, ))
    logging.info('done')

def main():
    logging.basicConfig(level=logging.INFO)

    db = mysql.connector.connect(
        host=config.MYSQL_HOST,
        port=config.MYSQL_PORT,
        user=config.MYSQL_USER,
        password=config.MYSQL_PASSWORD,
        database=config.MYSQL_DATABASE,
        charset='utf8mb4',
        sql_mode='TRADITIONAL,NO_AUTO_VALUE_ON_ZERO,ONLY_FULL_GROUP_BY',  # kamipo TRADITIONAL
        autocommit=True,
    )

    while True:
        time.sleep(1)

        request_id = undertake_request(db=db)
        if request_id is not None:
            try:
                data = serve_request(request_id, db=db)
            except:
                cur = db.cursor()
                cur.execute('UPDATE jobs SET assigned_to = NULL WHERE request_id = %s', (request_id, ))
                logging.info('cancel request %d', request_id)
                raise

if __name__ == '__main__':
    main()

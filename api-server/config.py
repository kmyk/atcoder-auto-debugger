import os
MYSQL = {
    'host': os.environ.get('MYSQL_HOST', 'localhost'),
    'port': os.environ.get('MYSQL_PORT', 3306),
    'user': os.environ.get('MYSQL_USER', 'user'),
    'password': os.environ.get('MYSQL_PASSWORD', 'password'),
    'database': os.environ.get('MYSQL_DATABASE', 'database'),
}

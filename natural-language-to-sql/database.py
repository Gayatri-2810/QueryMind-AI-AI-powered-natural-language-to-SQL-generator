"""Short-lived MySQL connections using the dedicated SELECT-only account."""
import os
from contextlib import closing
import mysql.connector
import pandas as pd


def connect():
    if os.getenv('DB_USER', '').lower() == 'root':
        raise ValueError('Use the nl_sql_reader account, not root.')
    return mysql.connector.connect(
        host=os.getenv('DB_HOST', 'localhost'),
        port=int(os.getenv('DB_PORT', '3306')),
        user=os.getenv('DB_USER', 'nl_sql_reader'),
        password=os.environ['DB_PASSWORD'],
        database=os.getenv('DB_NAME', 'nl_sql_demo'),
        connection_timeout=10,
        autocommit=True,
        charset='utf8mb4',
    )


def get_schema() -> str:
    """Read actual column names/types from MySQL, not a prompt constant."""
    with closing(connect()) as connection, closing(connection.cursor()) as cursor:
        cursor.execute('SHOW COLUMNS FROM employees')
        return 'TABLE employees (\n' + ',\n'.join(
            f'  {row[0]} {row[1]}' + (' PRIMARY KEY' if row[3] == 'PRI' else '')
            for row in cursor.fetchall()
        ) + '\n)'


def execute_query(sql: str, max_rows: int, timeout_ms: int) -> pd.DataFrame:
    if not 1 <= timeout_ms <= 60000:
        raise ValueError('QUERY_TIMEOUT_MS must be between 1 and 60000.')
    with closing(connect()) as connection, closing(connection.cursor()) as cursor:
        # Server-enforced timeout for SELECT statements (Oracle MySQL 5.7.8+).
        cursor.execute('SET SESSION MAX_EXECUTION_TIME = %s', (timeout_ms,))
        connection.start_transaction(readonly=True)
        try:
            cursor.execute(sql)
            columns = [column[0] for column in cursor.description]
            rows = cursor.fetchmany(max_rows)
            return pd.DataFrame(rows, columns=columns)
        finally:
            connection.rollback()

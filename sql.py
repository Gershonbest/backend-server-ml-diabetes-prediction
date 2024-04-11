import mysql.connector
from mysql.connector.errors import ProgrammingError
# PermissionError()
db_connection = mysql.connector.connect(
    host='localhost',
    user='root',
    password='gershblocks',
    database='health_log'
)
db_cursor = db_connection.cursor()
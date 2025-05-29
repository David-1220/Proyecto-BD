import oracledb

def get_connection():
    connection = oracledb.connect(
        user="SL",
        password="sl",
        dsn="localhost:1521/xepdb1"  
    )
    return connection

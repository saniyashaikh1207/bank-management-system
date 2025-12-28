
# database.py


import pyodbc

SQL_DRIVER = "ODBC Driver 17 for SQL Server"
SQL_SERVER = r"AYAN\SQLEXPRESS"
SQL_DATABASE = "Bank"


def create_connection():
    try:
        return pyodbc.connect(
            f"DRIVER={{{SQL_DRIVER}}};"
            f"SERVER={SQL_SERVER};"
            f"DATABASE={SQL_DATABASE};"
            "Trusted_Connection=yes;"
        )
    except pyodbc.Error as e:
        print("Database connection failed:", e)
        return None


def db_query(query, params=None, fetch=True):
    conn = create_connection()
    if not conn:
        return []

    try:
        cursor = conn.cursor()

        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)

        if fetch:
            result = cursor.fetchall()
        else:
            result = []

        conn.commit()
        return result

    except pyodbc.Error as e:
        conn.rollback()
        print("SQL execution error:", e)
        return []

    finally:
        conn.close()

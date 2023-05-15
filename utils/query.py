import psycopg2
from psycopg2 import Error

# CARA GUNAIN DI VIEWS
# 1. import utils-nya
# from utils.query import *
# 2. retreive datanya sebagai list 
# lst = execute_query("SELECT * FROM ATLET WHERE negara_asal='Indonesia';")

try:
    # Connect to an existing database
    connection = psycopg2.connect(user="postgres",
                                password="FPIEI3SWrANKKqu",
                                host="db.vzlihbczeroazalcaazw.supabase.co",
                                port="5432",
                                database="postgres")

    # Create a cursor to perform database operations
    cursor = connection.cursor()
    
    # Print PostgreSQL details
    print("PostgreSQL server information")
    print(connection.get_dsn_parameters(), "\n")

    # Executing a SQL query
    cursor.execute("SELECT version();")

    # Fetch result
    record = cursor.fetchone()
    print("You are connected to - ", record, "\n")

    cursor.execute("SET search_path TO BADMINTON")

except (Exception, Error) as error:
    print("Error while connecting to PostgreSQL", error)

def execute_query(query:str):
    query = query.strip()
    if not (query.endswith(";")):
        query += ";"
    cursor.execute(query)
    if (query.upper().startswith("SELECT")):
        return cursor.fetchall()
    elif (query.upper().startswith("INSERT")) or (query.upper().startswith("UPDATE")):
        connection.commit()

def list_tup_to_list_list(lst):
    ret = []
    for x in lst:
        ret.append(list(x))
    return ret
    
def iterate_list(lst):
    for x in lst:
        print(x)
    print()

def exec_and_print(query:str):
    iterate_list(execute_query(query))

# test
if __name__ == '__main__':
    exec_and_print("SELECT * FROM ATLET WHERE negara_asal='Indonesia';")
    exec_and_print("SELECT * FROM ATLET;")
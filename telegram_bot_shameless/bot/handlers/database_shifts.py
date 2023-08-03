from dotenv import load_dotenv
import os
import asyncio
import aiomysql
import re

# sql statements
count_shifts_sql = """
            SELECT COUNT(*)
            FROM shifts;
"""
select_shifts_sql = """
            SELECT *
            FROM shifts;
"""
get_recent_shifts_sql = """
            SELECT *
            FROM recent_shifts;
"""
clean_recent_shifts = """
            DELETE
            FROM recent_shifts;
"""
add_user_id_sql = """
            INSERT INTO user_ids
            (user_id)
            VALUES (%s);
"""
is_user_subscribed_sql = """
            SELECT *
            FROM user_ids
            WHERE user_id = %s;
"""
delete_user_id_sql = """
            DELETE
            FROM user_ids
            WHERE user_id = %s;
"""
get_all_users_ids_sql = """
            SELECT *
            FROM user_ids;
"""
# load password from .env file
load_dotenv('.env')
db_password = os.getenv('DB_PASSWORD')
db_user = os.getenv('DB_USER')
db_name = os.getenv('DB_NAME')
#connect to db
loop = asyncio.get_event_loop()
db_connection = None

async def connect_to_database():
    global db_connection
    if db_connection is None:
        db_connection = await aiomysql.connect(
            host='localhost',
            user=db_user,
            password=db_password,
            db=db_name,
            loop=loop,
            autocommit=True,
        )
    return db_connection

# function for sql code without output
async def execute_sql(connection, sql, args=None):
    async with connection.cursor() as cursor:
        if args is not None:
            await cursor.execute(sql, args)
        else:
            await cursor.execute(sql)
# function for sql code with output
async def fetch_sql(connection, sql, args=None):
    async with connection.cursor() as cursor:
        if args is not None:
            await cursor.execute(sql, args)
            result = await cursor.fetchall()
        else:
            await cursor.execute(sql)
            result = await cursor.fetchall()
    return result

async def get_shifts_by_conditions(connection, conditions_variables):
    # unpack list with variables
    date, position, shift_size = conditions_variables
    # base sql statement to which will be added conditions
    base_statement_sql = """
SELECT *
FROM shifts
WHERE"""
    
    # handle date
    one_date_re = r'\d{4}-\d{2}-\d{2}'
    interval_date_re = r'\d{4}-\d{2}-\d{2}-\d{4}-\d{2}-\d{2}'
    match_first = re.match(one_date_re, date)
    match_second = re.match(interval_date_re, date)

    added_date, added_position = False, False
   
    # firstly check interval dates, doesn't work in another order!
    if match_second:
        dates = date.split('-')
        start_date = '-'.join(dates[:3])
        end_date = '-'.join(dates[3:])
        date_sql = f" date BETWEEN '{start_date}' AND '{end_date}'"
        base_statement_sql += date_sql
        added_date = True
    elif match_first:
        date_sql = f" date = '{date}'"
        base_statement_sql += date_sql
        added_date = True

    # handle position
    if position != 'Любая':
        stagehands_position = 'Stagehands - ' + position
        position_sql = f"position = '{stagehands_position}'"
        if added_date:
            base_statement_sql += ' AND'
        base_statement_sql += f" {position_sql}"
        added_position = True

    # handle shift_size
    if shift_size != "Любые" and position != 'Crewboss':
        if shift_size == "Маленькие":
            if added_position or added_date:
                base_statement_sql += ' AND'
            small_shifts_sql = f" CAST(SUBSTR(capacity, INSTR(capacity, '/') + 1) AS UNSIGNED) <= 10"
            base_statement_sql += small_shifts_sql
        elif shift_size == 'Большие':
            if added_position or added_date:
                base_statement_sql += ' AND'
            big_shifts_sql = f" CAST(SUBSTR(capacity, INSTR(capacity, '/') + 1) AS UNSIGNED) > 11"
            base_statement_sql += big_shifts_sql
   
    # is there is no conditionds added, delete WHERE keyword
    if not base_statement_sql.strip():
        base_statement_sql = "SELECT * FROM shifts"
    else:
        base_statement_sql = base_statement_sql.rstrip("WHERE")
    
    # add ; to the end of sql statement
    base_statement_sql += ';'

    # execute sql statement
    result = await fetch_sql(connection, base_statement_sql)
    
    return result

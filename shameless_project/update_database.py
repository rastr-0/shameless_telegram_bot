# this file stands for updating database
# inserting, updating and deleting shifts web-scraped shifts

import extract_shifts
import datetime
from datetime import datetime as dt
import asyncio
import aiomysql
import os
from dotenv import load_dotenv

# load password from .env file
load_dotenv('.env')
db_password = os.getenv('DB_PASSWORD')
db_user = os.getenv('DB_USER')
db_name = os.getenv('DB_NAME')


#connect to db
async def connect_to_database(loop):
    connection = await aiomysql.connect(
        host='localhost',
        user=db_user,
        password=db_password,
        db=db_name,
        loop=loop,
        autocommit=True,
    )
    return connection

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

async def update_database(shifts, loop):
    # today's date
    today = datetime.date.today()

    # connect to the database
    conn = await connect_to_database(loop)

    # SQL statements
    select_all_shifts_sql = """
                    SELECT *
                    FROM shifts;
    """
    select_shift_sql = """
                    SELECT *
                    FROM shifts
                    WHERE name = %s AND date = %s
                    AND time = %s AND place = %s
                    AND position = %s;
    """

    insert_shift_sql = """
                    INSERT INTO shifts
                    (name, date, time, place, position, capacity)
                    VALUES (%s, %s, %s, %s, %s, %s);
    """
    update_capacity_sql = """
                    UPDATE shifts
                    SET capacity = %s
                    WHERE name = %s AND date = %s AND time = %s
                    AND place = %s AND position = %s;
    """
    delete_shift_sql = """
                    DELETE FROM shifts
                    WHERE name = %s AND date = %s
                    AND time = %s AND place = %s
                    AND position = %s AND capacity = %s;
    """
    insert_recent_shifts_db_sql = """
                    INSERT INTO recent_shifts
                    (name, date, time, place, position, capacity)
                    VALUES (%s, %s, %s, %s, %s, %s)
    """
    # add shifts to the database
    for shift in shifts:
        result = await fetch_sql(conn, select_shift_sql, shift[0:5])
        # checking for new shifts
        if not result:
            # add shift to the main database (shifts)
            await execute_sql(conn, insert_shift_sql, shift)
            #print(f'The shift [{shift[0]}] has been added - {dt.now()}')
            # add shift to the second database (recent_shifts) for sending
            await execute_sql(conn, insert_recent_shifts_db_sql, shift)
        # checking for changing of the capacity for the same shifts
        else:
            if len(result) > 1:
                list_result = list(result[0])
                if list_result[5] != shift[5]:
                    await execute_sql(conn, update_capacity_sql, (shift[5],) + tuple(shift[0:5]))
                    #print(f"The capacity for [{shift[0]}] has been changed - {dt.now()}")
            #else:
                #print(f'The shift [{shift[0]}] is already in the db - {dt.now()}')

    # get current shifts in the database
    shifts_in_database = await fetch_sql(conn, select_all_shifts_sql)
    # convert types for right comparison (change list to tuple and datetime.date to str)
    web_shifts_tuples = [tuple(shift) for shift in shifts]
    converted_shifts_db = []
    for shift_db in shifts_in_database:
        name, date, time, place, position, capacity = shift_db
        converted_date = date.strftime('%Y-%m-%d')
        converted_shifts_db.append((name, converted_date, time, place, position, capacity))

    # delete shifts that are out of date or ain't on the web-site anymore
    shifts_to_delete = [
                shift_db for shift_db in converted_shifts_db
                if shift_db[1] < str(today) or shift_db not in web_shifts_tuples
    ]
    for shift in shifts_to_delete:
        await execute_sql(conn, delete_shift_sql, shift)
        #print(f'The shift [{shift[0]}] has been deleted - {dt.now()}')

    print('script was executed')

    conn.close()

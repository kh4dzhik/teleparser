from client import client
from db import db_connection, cursor, execute_query
import re
import time
from sqlite3 import OperationalError


def delete_table(table):
    del_query = f"DROP TABLE {table};"
    execute_query(del_query)


def create_users_table(table_name):
    create_table_query = f"""CREATE TABLE {table_name} (
        id INTEGER,
        username TEXT,
        phone TEXT,
        first_name TEXT,
        last_name TEXT
    );"""
    execute_query(create_table_query)


def create_posts_table(table_name):
    create_table_query = f"""CREATE TABLE {table_name} (
        message TEXT,
        mediapath TEXT
    );"""
    execute_query(create_table_query)


async def get_users():
    name_or_link = input("enter chanel name: ").strip()
    print(name_or_link)
    limit = input("all or limit num: ").strip()

    if limit == "all":
        limit = None
    elif limit == '':
        print("enter sthg")
        exit()
    else:
        limit = int(limit)

    users = await client.get_participants(name_or_link, limit=limit)
    return users 


def quotes_replacer(data):
    final_data = [data.username, data.phone, data.first_name, data.last_name]
    for u in range(len(final_data)):
        if final_data[u] == None: continue
        final_data[u] = final_data[u].replace("'", "")
        final_data[u] = final_data[u].replace('"', "")
    return final_data 


def insert_users_data(users, table_name):
    insert_query = f"INSERT INTO {table_name} (id, username, phone, first_name, last_name) VALUES"
    for user in users:
        data = quotes_replacer(user)     
        insert_query += f" ({user.id}, '{data[0]}', '{data[1]}', '{data[2]}', '{data[3]}'),"
    insert_query = insert_query[:-1]
    insert_query += ';'

    execute_query(insert_query)
    print("гуд нахой")



async def update_users_table(table_name):
    users = await get_users()
    get_ids_query = "SELECT id FROM {}".format(table_name)
    try:
        cursor.execute(get_ids_query)
    except:
        print("before create a table")
        return None

    users_to_add = []
    db_ids = [i[0] for i in cursor.fetchall()]
    new_u_ids = [user.id for user in users] 

    for user in users:
        if user.id not in db_ids:
            users_to_add.append(user)

    if len(users_to_add) != 0:
        insert_users_data(users_to_add, table_name)     
    else:
        print("there is no to add")

    del_query = "DELETE FROM `{}` WHERE 'id' IN (".format(table_name)
    qlen = len(del_query)
    for id in db_ids:
        if id not in new_u_ids:
            del_query += f"'{id}', "
    if len(del_query) == qlen: return 0
    del_query = del_query[:-2] + ");"
    print(del_query)
    execute_query(del_query) 



async def get_and_insert_posts_to_db(table_name):
    chanel_name = input("chanel name: ").strip()
    lim = int(input("posts limit: "))

    posts = await client.get_messages(chanel_name, limit=lim)
    insert_query = f"INSERT INTO {table_name} (message, mediapath) VALUES"

    for p in posts:
        if p.media is not None:
            mediapath = await p.download_media("./media/")
            insert_query += f" ('{p.message}', '{mediapath}'),"
        else:
            insert_query += f" ('{p.message}', 'None'),"
    insert_query = insert_query[:-1]
    insert_query += ';'
    print(insert_query)
    execute_query(insert_query)


def table_list(flagfor):
    execute_query("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    table_list = ""
    for i in range(len(tables)):
        table_list += f"{i+1}) {tables[i][0]}\n"

    if flagfor == "show": print(table_list) 
    elif flagfor == "choise":
        choise = int(input(table_list))
        choise = tables[choise-1][0]
        return choise


async def run():

    while True:
        way = input("1) show tables\n2) delete data\n3) create users table and write to \n4) update users data\n5) create table and insert messages \n0) exit\n").strip()
        if way == "1": table_list(flagfor="show")

        elif way == "2":
            table = table_list(flagfor="choise")
            delete_table(table)

        elif way == "3":
            try:
                table_list(flagfor="show")
                new_table_name = input("new table name: ").strip()
                create_users_table(new_table_name)
                users = await get_users()
            except OperationalError:
                print("table is already exists. update or delete  and in the same way!!!")
                continue
            except:
                print("users are privet")
                continue
            insert_users_data(users, new_table_name)

        elif way == "4":
            table_name = table_list(flagfor="choise")
            await update_users_table(table_name)

        elif way == "5":
            table_list(flagfor="show")
            try:
                new_table_name = input("new table name: ").strip()
                create_posts_table(new_table_name)
            except:
                print("table is already exists")
            await get_and_insert_posts_to_db(new_table_name)

        else:
            break

    cursor.close()
    db_connection.close()

    

client.loop.run_until_complete(run())
client.disconnect()
















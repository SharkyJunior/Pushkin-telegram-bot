from peewee import MySQLDatabase
from dotenv import load_dotenv
import os

load_dotenv()

id_list = []

if __name__ == '__main__':
    db = MySQLDatabase('mysql', user='root', password=os.getenv('DB_PASS'),
                       host='localhost', port=3306)

    cur = db.cursor()
    cur.execute('SELECT id FROM artwork;')
    ids = cur.fetchall()
    id_list = list(i[0] for i in ids)
    print(id_list)

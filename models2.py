from peewee import (PostgresqlDatabase, Model, TextField,
                    IntegerField)
from dotenv import load_dotenv

import os

load_dotenv()
db_name = os.getenv('DB_NAME')


db = PostgresqlDatabase(os.getenv('DB_NAME'),
                        host=os.getenv('DB_HOST'),
                        port=int(os.getenv('DB_PORT'))
                        )


class BaseModel(Model):
    name = TextField()
    description = TextField()

    class Meta:
        database = db
        db_table = db_name


class Hall(BaseModel):
    pass


class Author(BaseModel):
    pass


class Collection(BaseModel):
    pass


class Link(BaseModel):
    pass


class Exhibit(BaseModel):
    inv_number = IntegerField()


db.connect()

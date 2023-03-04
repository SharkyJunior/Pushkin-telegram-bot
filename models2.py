from peewee import (PostgresqlDatabase, Model, TextField,
                    IntegerField, ForeignKeyField)
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
    hall_id = IntegerField()


class Author(BaseModel):
    author_id = IntegerField()


class Collection(BaseModel):
    collection_id = IntegerField()


class Link():
    link_id = IntegerField()
    link = TextField()
    comment = TextField()


class Exhibit(BaseModel):
    inv_number = IntegerField()
    theme = TextField()
    year = IntegerField()
    period = TextField()
    scan = TextField()
    technique = TextField()
    size = TextField()
    notes = TextField()
    type = TextField()
    country = TextField()
    specificity = TextField()
    author_id = ForeignKeyField("author_id")
    hall_id = ForeignKeyField("hall_id")
    collection_id = ForeignKeyField("collection_id")


db.connect()

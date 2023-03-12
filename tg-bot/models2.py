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
    pass


class Author(BaseModel):
    pass


class Collection(BaseModel):
    pass


class Link(BaseModel):
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
    author_id = ForeignKeyField(Author, backref='exhibits')
    hall_id = ForeignKeyField(Hall, backref='exhibits')
    collection_id = ForeignKeyField(Collection, backref='exhibits')


db.connect()

db.create_tables([Hall, Author, Collection, Link, Exhibit])
from peewee import *

class BaseModel(Model):
    name = TextField()
    description = TextField()
    
    class Meta:
        data
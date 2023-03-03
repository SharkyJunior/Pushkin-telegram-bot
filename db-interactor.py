from models import Exhibit, db
from sqlalchemy.orm import sessionmaker


class DBInteractor:
    def __init__(self):
        pass

    def getDataByName(self, name):
        Session = sessionmaker(bind=db)
        session = Session()
        q = session.query(Exhibit)
        print(q.all())


obj = DBInteractor()
obj.getDataByName('nnnnmn')

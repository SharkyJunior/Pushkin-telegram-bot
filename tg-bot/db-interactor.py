from models2 import Exhibit


class DBInteractor:
    def __init__(self):
        pass

    def add(self, obj, inv_number, theme, year, period, scan,
            technique, size, notes, type, country, specificity,
            author_id, hall_id, collection_id):
        obj = Exhibit.create(inv_number=inv_number, theme=theme, year=year,
                             period=period, scan=scan, technique=technique,
                             size=size, notes=notes, type=type,
                             country=country, specificity=specificity,
                             author_id=author_id, hall_id=hall_id,
                             collection_id=collection_id)
        obj.save()

    def getNameByScan(self, sc):
        number = Exhibit.select(Exhibit.inv_number).where(Exhibit.scan == sc)
        return number

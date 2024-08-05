from pymongo import MongoClient

class MongoDBConnection:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(MongoDBConnection, cls).__new__(cls)
            cls._instance.client = MongoClient('mongodb://localhost:27017/')
            cls._instance.db = cls._instance.client['seminar_hall_booking']
        return cls._instance

    @property
    def database(self):
        return self.db

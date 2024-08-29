from pymongo import MongoClient,ReturnDocument
from datetime import datetime, timezone
import os


class BookingDatabase:
    _instance = None

    def __new__(cls):
        """
        Ensure that only one instance of the BookingDatabase class exists.
        
        Returns:
            BookingDatabase: The singleton instance of the BookingDatabase class.
        """
        if cls._instance is None:
            cls._instance = super(BookingDatabase, cls).__new__(cls)
            mongo_uri = os.getenv('MONGO_URI', 'mongodb://localhost:27017/')
            cls._instance.client = MongoClient(mongo_uri)
            cls._instance.db = cls._instance.client['seminar_hall_booking']
            cls._instance.bookings = cls._instance.db.bookings
        return cls._instance

    def delete_database(self) -> dict:
        """
        Deletes all documents in the bookings collection.

        Returns:
            dict: A dictionary containing the deletion result details.
        """
        return self.bookings.delete_many({})

    def find(self, query):
        return self.bookings.find(query)

    def find_one(self,query):
        return self.bookings.find_one(query)

    def update_one(self, query, update, upsert = False):
        return self.bookings.update_one(query, update, upsert = upsert)

    def find_one_and_delete(self, query) -> dict:
        return self.bookings.find_one_and_delete(query)
    


from pymongo import MongoClient
from datetime import datetime, timezone


class BookingDatabase:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(BookingDatabase, cls).__new__(cls)
            cls._instance.client = MongoClient('mongodb://localhost:27017/')
            cls._instance.db = cls._instance.client['seminar_hall_booking']
            cls._instance.bookings = cls._instance.db.bookings
        return cls._instance

    def delete_database(self):
        return self.bookings.delete_many({})
    
    def insert_hall_booking(self,data):
        result = self.bookings.insert_one(data)
        booking_id = str(result.inserted_id)[-6:]
        self.bookings.update_one({'_id': result.inserted_id}, {'$set': {'booking_id': booking_id}})
        return booking_id

    def fetch_available(self,start_time, end_time):
        return self.bookings.find({
            "$or": [
                {"start_time": {"$lte": end_time, "$gte": start_time}},
                {"end_time": {"$lte": end_time, "$gte": start_time}}
            ]})

    def fetch_bookings(self,start_date, end_date):
        start_date_obj = start_date+"T00:00:00"
        end_date_obj = end_date+"T23:59:59"
        return self.bookings.find({
            "$and": [
            {"start_time": {"$lte": end_date_obj}},
            {"end_time": {"$gte": start_date_obj}}
            ]})
    
    def find_booking(self,booking_id):
        return self.bookings.find_one({'booking_id': booking_id})
    
    def delete_booking(self, booking_id):
        return self.bookings.delete_one({'booking_id': booking_id})
    
    def find_conflicting_bookings(self,hall_id, booking_id,new_start_time, new_end_time):
        query = {
                "hall_id": hall_id,
                "booking_id": {"$ne": booking_id},  # Excluding the provided booking_id
                "$or": [
                    {"start_time": {"$lt": new_end_time}, "end_time": {"$gt": new_start_time}}
                ]}
        return self.bookings.find_one(query)
    
    def update_booking(self, booking_id, new_start_time, new_end_time):
        return self.bookings.update_one(
                {'booking_id': booking_id},
                {'$set': {'start_time': new_start_time, 'end_time': new_end_time}}
            )

    def get_lock(self, hall_id, session):
        return self.db['locks'].insert_one(
            {'_id': f'lock_{hall_id}', 'locked_at': datetime.now(timezone.utc)},
            session=session)
    
    def delete_lock(self, hall_id, session):
        self.db['locks'].delete_one({'_id': f'lock_{hall_id}'}, session=session)




from database.db_connection import MongoDBConnection
from models.booking import Booking
from datetime import datetime
import threading

class BookingService:
    def __init__(self):
        self.db = MongoDBConnection().database
        self.lock = threading.Lock()

    def fetch_available_halls(self, start_time, end_time):
        bookings = self.db.bookings.find({
            "$or": [
                {"start_time": {"$lt": end_time, "$gt": start_time}},
                {"end_time": {"$lt": end_time, "$gt": start_time}}
            ]
        })
        booked_halls = [booking['hall_id'] for booking in bookings]
        all_halls = ['A', 'B', 'C', 'D', 'E', 'F']
        available_halls = [hall for hall in all_halls if hall not in booked_halls]
        return available_halls

    def book_hall(self, hall_id, start_time, end_time):
        with self.lock:
            if hall_id in self.fetch_available_halls(start_time, end_time):
                booking = Booking(hall_id, start_time, end_time)
                self.db.bookings.insert_one(booking.__dict__)
                return "Booking successful"
            else:
                return "Hall is already booked for the given time slot"

from database.db_connection import MongoDBConnection
from utils.lock_manager import LockManager
from models.booking import Booking
from collections import defaultdict
from threading import Lock
from datetime import datetime
import threading
import time

class BookingService:
    
    _instance = None
    _lock = Lock()

    

    def __new__(cls, *args, **kwargs):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super().__new__(cls)
                cls._instance._initialize()
        return cls._instance
    
    def _initialize(self):
        self.lock_service = LockManager()
        self.db = MongoDBConnection().database
        # self.lock = threading.Lock()
        self.locks = defaultdict(Lock)
        self.all_halls = ['A', 'B', 'C', 'D', 'E', 'F']

    def fetch_available_halls(self, start_time, end_time):
        bookings = self.db.bookings.find({
            "$or": [
                {"start_time": {"$lte": end_time, "$gte": start_time}},
                {"end_time": {"$lte": end_time, "$gte": start_time}}
            ]
        })
        booked_halls = [booking['hall_id'] for booking in bookings]
        # all_halls = 
        available_halls = [hall for hall in self.all_halls if hall not in booked_halls]
        return available_halls

    def book_hall(self, hall_id, start_time, end_time,thread):
        # with self.lock:
        # LockManager.acquire_lock()
        # lock_service = LockManager()
        res = self.lock_service.acquire_lock(hall_id, start_time, end_time)
        print(res)
        # if self.lock_service.acquire_lock(hall_id, start_time, end_time):
        if res:
            # print(thread," got lock")
            try:
                if hall_id in self.fetch_available_halls(start_time, end_time):
                    print("hall available")
                    booking = Booking(hall_id, start_time, end_time)
                    time.sleep(7)
                    result = self.db.bookings.insert_one(booking.__dict__)
                    booking.set_booking_id(result.inserted_id)
                    self.db.bookings.update_one({'_id': result.inserted_id}, {'$set': {'booking_id': booking.booking_id}})
                    return f"Booking successful. Booking ID: {booking.booking_id}"
                else:
                    return "Hall is already booked for the given time slot"
            finally:
                self.lock_service.release_lock(hall_id, start_time, end_time)
        else:
            return "Could not acquire lock for the given time slot"
            
    def book_multiple_halls(self, bookings):
        results = []
        for booking in bookings:
            hall_id = booking['hall_id']
            start_time = booking['start_time']
            end_time = booking['end_time']
            result = self.book_hall(hall_id, start_time, end_time)
            results.append({ "hall_id": hall_id, "result": result })
        return results
    

    
    def fetch_all_booked_halls(self, start_date, end_date):

        try:
            # print("w0")
            # start_date_obj = datetime.strptime(start_date, '%Y-%m-%dT%H:%M:%S')
            start_date_obj = start_date+"T00:00:00"
            end_date_obj = end_date+"T23:59:59"
            # print("w1")
            # end_date_obj = datetime.strptime(end_date, '%Y-%m-%dT%H:%M:%S')
            bookings = self.db.bookings.find({
                "$and": [
                {"start_time": {"$lte": end_date_obj}},
                {"end_time": {"$gte": start_date_obj}}
                ]
                # "$or": [
                #     {"start_time": {"$lte": start_date_obj}, "end_time": {"$gte": start_date_obj}},
                #     {"start_time": {"$lte": end_date_obj}, "end_time": {"$gte": end_date_obj}}
                # ]
            })
            # print(len(bookings))
            booked_records = []
            for booking in bookings:
                booked_records.append({
                    "booking_id": booking["booking_id"],
                    "hall_id": booking["hall_id"],
                    "start_time": booking["start_time"],
                    "end_time": booking["end_time"],
                })
            print("showing records...")
            # print(booked_records)
            for record in booked_records:
                print(record)
            return booked_records
        
        except Exception as e:
            print(f"An error occurred: {e}")
            return []

    # def cancel_booking(self, data):
    #     with self.lock:
    #         result = self.db.bookings.delete_one({'booking_id': data["booking_id"]})
    #         if result.deleted_count > 0:
    #             return f"Booking with ID {data["booking_id"]} has been canceled successfully."
    #         else:
    #             return f"Booking with ID {data["booking_id"]} not found."


    def cancel_booking(self, short_booking_id):
        lock_service = LockManager()

        # print("bk id-",short_booking_id)
        booking = self.db.bookings.find_one({'booking_id': short_booking_id})
        if not booking:
            return f"Booking with ID {short_booking_id} not found."

        hall_id = booking['hall_id']
        start_time = booking['start_time']
        end_time = booking['end_time']

        if lock_service.acquire_lock(hall_id, start_time, end_time):
            try:
                result = self.db.bookings.delete_one({'booking_id': short_booking_id})
                if result.deleted_count > 0:
                    return f"Booking with ID {short_booking_id} has been canceled successfully."
                else:
                    return f"Booking with ID {short_booking_id} not found."
            finally:
                lock_service.release_lock(hall_id, start_time, end_time)
        else:
            return "Could not acquire lock for the given time slot"


    def update_booking(self, short_booking_id, new_start_time, new_end_time):
        lock_service = LockManager()

        booking = self.db.bookings.find_one({'booking_id': short_booking_id})
        if not booking:
            return f"Booking with ID {short_booking_id} not found."

        hall_id = booking['hall_id']
        old_start_time = booking['start_time']
        old_end_time = booking['end_time']

        if (lock_service.acquire_lock(hall_id, old_start_time, old_end_time) and 
            lock_service.acquire_lock(hall_id, new_start_time, new_end_time)):
            try:
                # Check if the new time slot is available
                if hall_id in self.fetch_available_halls(new_start_time, new_end_time):
                    result = self.db.bookings.update_one(
                        {'booking_id': short_booking_id},
                        {'$set': {'start_time': new_start_time, 'end_time': new_end_time}}
                    )
                    if result.modified_count > 0:
                        return f"Booking with ID {short_booking_id} has been updated successfully."
                    else:
                        return f"Failed to update booking with ID {short_booking_id}."
                else:
                    return "The new time slot is not available for the selected hall."
            finally:
                lock_service.release_lock(hall_id, old_start_time, old_end_time)
                lock_service.release_lock(hall_id, new_start_time, new_end_time)
                # print("updated, locks released!")
        else:
            return "Could not acquire lock for the given time slot"
        







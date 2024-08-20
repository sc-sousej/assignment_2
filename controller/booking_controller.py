from database.db_module import BookingDatabase
from utils.lock_manager import LockManager
from models.booking import Booking
from collections import defaultdict
from threading import Lock
from utils.logger import setup_logger
from datetime import datetime
from models.halls import halls
import json



class BookingController:
    
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
        self.db = BookingDatabase()
        self.logger = setup_logger("booking_service.log")
        if self.db is None:
            self.logger.error("Connection with DB Failed!")
        # self.all_halls = ['A', 'B', 'C', 'D', 'E', 'F']

    def verify_time_range(self,start, end):  
        try:
            start_time = datetime.fromisoformat(start)
            end_time = datetime.fromisoformat(end)

            if end_time > start_time:
                return True
            return False
        except ValueError:
            self.logger.error("Date format Invalid")
            raise Exception(f"date format invalid")
        
        
    def delete_all_bookings(self):
        result = self.db.delete_database()
        return f"Deleted {result.deleted_count} bookings from the database."
    

    def fetch_available_halls(self, start_time, end_time):
        try:
            self.logger.info(f"Received fetch available hall request: Start: {start_time}, End: {end_time}")
            if not self.verify_time_range(start_time,end_time):
                return "Error: End time must be after start time. Please try again."
        except:
            self.logger.info(f"Fetch available hall failed!: Start: {start_time}, End: {end_time}")
            raise
        bookings = self.db.fetch_available(start_time,end_time)

        booked_halls = [booking['hall_id'] for booking in bookings]
        available_halls = [{'hall_id': hall.name, 'capacity': hall.value} for hall in halls if hall.name not in booked_halls]
        
        return available_halls
    

    def book_hall(self, hall_id, start_time, end_time):
        self.logger.info(f"Received booking request: Hall {hall_id}, Start: {start_time}, End: {end_time}")

        if not self.verify_time_range(start_time,end_time):
            return "Error: End time must be after start time. Please try again."

        if self.lock_service.acquire_lock(hall_id, start_time, end_time):
            try:
                available_halls = self.fetch_available_halls(start_time, end_time)
                available_hall_ids = [hall['hall_id'] for hall in available_halls]
                if hall_id in available_hall_ids:
                    booking = Booking(hall_id, start_time, end_time)
                    booking_id = self.db.insert_hall_booking(booking.__dict__)

                    self.logger.info(f"Booking successful for hall {hall_id}. Booking ID: {booking_id}")
                    return f"Booking successful for hall {hall_id}. Booking ID: {booking_id}"
                else:
                    return "Hall is already booked for the given time slot"
            except Exception as e:
                self.logger.error(f"Book hall failed! Hall {hall_id}, Start: {start_time}, End: {end_time}, Error: {e}")

            finally:
                self.lock_service.release_lock(hall_id, start_time, end_time)
        else:
            self.logger.error(f"Book: Lock aquire failed! Hall {hall_id}, Start: {start_time}, End: {end_time}")
            return "Could not acquire lock for the given time slot"
            
    
    def fetch_bookings(self, start_date, end_date):
        self.logger.info(f"Received fetch bookings request: Start: {start_date}, End: {end_date}")

        start_time = datetime.fromisoformat(start_date)
        end_time = datetime.fromisoformat(end_date)

        if end_time < start_time:
            return "Error: End time must be after start time. Please try again."

        try:
            bookings = self.db.fetch_bookings(start_date,end_date)
            # print("bkings===",bookings)
            booked_records = []
            for booking in bookings:
                booked_records.append({
                    "booking_id": booking["booking_id"],
                    "hall_id": booking["hall_id"],
                    "start_time": booking["start_time"],
                    "end_time": booking["end_time"],
                })
            self.logger.info(f"Fetch bookings success: Start: {start_date}, End: {end_date}")
            return booked_records
        
        except Exception as e:
            self.logger.error(f'Fetch bookings failed,  Start: {start_date}, End: {end_date}: {e}')
            return []


    def cancel_booking(self, short_booking_id):
        self.logger.info(f"Received cancellation request: Booking ID: {short_booking_id}")

        booking = self.db.find_booking(short_booking_id)
        if not booking:
            return f"Booking with ID {short_booking_id} not found."

        hall_id = booking['hall_id']
        start_time = booking['start_time']
        end_time = booking['end_time']

        if self.lock_service.acquire_lock(hall_id, start_time, end_time):
            try:
                result = self.db.delete_booking(short_booking_id)
                if result.deleted_count > 0:
                    return f"Booking with ID {short_booking_id} has been cancelled successfully."
                else:
                    return f"Booking with ID {short_booking_id} not found."
            finally:
                self.lock_service.release_lock(hall_id, start_time, end_time)
        else:
            self.logger.error(f'Cancellation: Lock aquire failed, Booking ID: {short_booking_id}')
            return "Could not acquire lock for the given time slot"


    def update_booking(self, short_booking_id, new_start_time, new_end_time):
        self.logger.info(f'Received update request: Booking ID: {short_booking_id}, Start: {new_start_time}, End: {new_end_time}')

        if not self.verify_time_range(new_start_time,new_end_time):
            return "Error: End time must be after start time. Please try again."
        
        booking = self.db.bookings.find_one({'booking_id': short_booking_id})
        if not booking:
            return f"Booking with ID {short_booking_id} not found."

        hall_id = booking['hall_id']
        booking_id = booking['booking_id']
        old_start_time = booking['start_time']
        old_end_time = booking['end_time']

        lock_conflict = not (new_end_time < old_start_time or new_start_time > old_end_time)
        lock_aquired = False

        if lock_conflict:
            print("lock conflict detected")
            lock_start_time = min(old_start_time,new_start_time)
            lock_end_time = min(old_end_time,new_end_time)
            if self.lock_service.acquire_lock(hall_id, lock_start_time, lock_end_time):
                lock_aquired = True
                # print("aquired lock by combing time slots")


        elif(self.lock_service.acquire_lock(hall_id, old_start_time, old_end_time) and 
            self.lock_service.acquire_lock(hall_id, new_start_time, new_end_time)):
                lock_aquired = True
                # print("both lock aquired for updating")

        if lock_aquired:
            try:
                conflicting_booking = self.db.find_conflicting_bookings(hall_id,booking_id, new_start_time,new_end_time)

                if conflicting_booking is None:
                    result = self.db.update_booking(booking_id,new_start_time,new_end_time)
                    if result.modified_count > 0:
                        self.logger.info(f'Update success, Booking ID: {booking_id}, Start: {new_start_time}, End: {new_end_time}')
                        return f"Booking with ID {short_booking_id} has been updated successfully."
                    else:
                        return f"Failed to update booking with ID {short_booking_id}."
                else:
                    return "The new time slot is not available for the selected hall."
            finally:
                if not lock_conflict:
                    self.lock_service.release_lock(hall_id, old_start_time, old_end_time)
                    self.lock_service.release_lock(hall_id, new_start_time, new_end_time)
                else:
                    self.lock_service.release_lock(hall_id, lock_start_time, lock_end_time)
        else:
            self.logger.error(f'Update: Lock aquire failed, Booking ID: {booking_id}, Start: {new_start_time}, End: {new_end_time}')
            return "Could not acquire lock for the given time slot"
        







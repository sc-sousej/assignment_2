from database.db_module import BookingDatabase
from models.booking import Booking
from utils.logger import setup_logger
from utils.lock_manager import LockManager
from datetime import datetime
from models.halls import halls
from threading import Lock
from bson.objectid import ObjectId


class BookingController:
    
    _instance = None
    _lock = Lock()

    def __new__(cls, *args, **kwargs):
        """
        Ensure that only one instance of the BookingController class exists.
        
        Returns:
            BookingController: The singleton instance of the BookingController class.
        """
        with cls._lock:
            if cls._instance is None:
                cls._instance = super().__new__(cls)
                cls._instance._initialize()
        return cls._instance
    

    def _initialize(self) -> None:
        """
        Initialize the BookingController instance by setting up the database connection, lock service 
        and logger. Logs an error if the database connection fails.
        """
        self.db = BookingDatabase()
        self.lock_service = LockManager()
        self.logger = setup_logger("booking_controller.log")
        if self.db is None:
            self.logger.error("Connection with DB Failed!")


    def verify_time_range(self, start, end) -> bool:  
        """
        Verify that the end time is after the start time.

        Args:
            start (str): ISO 8601 formatted start time string.
            end (str): ISO 8601 formatted end time string.

        Returns:
            bool: True if the end time is after the start time, False otherwise.

        Raises:
            ValueError: If the date format is invalid.
        """
        try:
            start_time = datetime.fromisoformat(start)
            end_time = datetime.fromisoformat(end)

            if end_time > start_time:
                return True
            return False
        except ValueError:
            self.logger.error("Date format Invalid")
            raise Exception(f"date format invalid")


    def delete_all_bookings(self) -> str:
        """
        Delete all bookings from the database.

        Returns:
            str: A message indicating how many bookings were deleted.
        """
        result = self.db.delete_database()
        return f"Deleted {result.deleted_count} bookings from the database."
    

    def book_hall(self, hall_id, start_time, end_time, capacity) -> str:
        """
        Attempt to book a hall for the given time range. Handles concurrency using a lock.

        Args:
            hall_id (str): The ID of the hall to be booked.
            start_time (str): ISO 8601 formatted start time string.
            end_time (str): ISO 8601 formatted end time string.

        Returns:
            str: A message indicating whether the booking was successful or an error occurred.
        """
        self.logger.info(f"Received booking request: Hall {hall_id}, Start: {start_time}, End: {end_time}, capacity: {capacity}")

        if not self.verify_time_range(start_time, end_time):
            return "Error: End time must be after start time. Please try again."
        
        if not halls[hall_id].value >= capacity:
            return "Error: This hall does not have required capacity"
        
        
        if self.lock_service.acquire_lock(hall_id, start_time, end_time):
            try:
                # make an object of Booking to insert in DB
                booking = Booking(hall_id, start_time, end_time, capacity)

                # query to search for conflicting bookings
                search_query = {
                    "hall_id": hall_id,
                    "$and": [
                        {"start_time": {"$lt": end_time}}, 
                        {"end_time": {"$gt": start_time}}
                    ]}
                # query to insert Booking object in DB
                update_query = {
                    "$setOnInsert": booking.__dict__
                    }
                
                result = self.db.update_one(search_query, update_query, upsert=True)

                if result.matched_count > 0:
                    self.logger.info(f"Booking Unsuccessful for hall {hall_id}. Hall already booked!")
                    return "Hall already booked for this slot"
                else:
                    # booking successful
                    booking_id = str(result.upserted_id)
                    self.logger.info(f"Booking successful for hall {hall_id}. Booking ID: {booking_id}")

                    return f"Booking successful for hall {hall_id}. Booking ID: {booking_id}"
                
            except Exception as e:
                self.logger.error(f"Book hall failed! Hall {hall_id}, Start: {start_time}, End: {end_time}, Error: {e}")

            finally:
                self.lock_service.release_lock(hall_id, start_time, end_time)
        else:
            self.logger.error(f"Book: Lock aquire failed! Hall {hall_id}, Start: {start_time}, End: {end_time}")
            return "Could not acquire lock for the given time slot"


    def fetch_available_halls(self, start_time, end_time, capacity) -> list[dict]:
        """
        Fetch all available halls for the given time range.

        Args:
            start_time (str): ISO 8601 formatted start time string.
            end_time (str): ISO 8601 formatted end time string.

        Returns:
            list[dict]: A list of dictionaries with available hall information.
        """
        try:
            self.logger.info(f"Received fetch available hall request: Start: {start_time}, End: {end_time}")
            if not self.verify_time_range(start_time, end_time):
                return "Error: End time must be after start time. Please try again."
        except:
            self.logger.info(f"Fetch available hall failed!: Start: {start_time}, End: {end_time}")
            raise
        # query to find all halls available for a time slot
        fetch_query = {
            "$or": [
                {"start_time": {"$lte": end_time, "$gte": start_time}},
                {"end_time": {"$lte": end_time, "$gte": start_time}}
            ]}
        bookings = self.db.find(fetch_query)
        booked_halls = [booking['hall_id'] for booking in bookings]
        # showing only those halls which have capacity greater than or equal to required capacity
        available_halls = [{'hall_id': hall.name, 'capacity': hall.value} for hall in halls if (hall.name not in booked_halls and hall.value >= capacity)]
        
        return available_halls

    
    def fetch_bookings(self, start_date, end_date) -> list[dict]:
        """
        Fetch all bookings within the specified date range.

        Args:
            start_date (str): ISO 8601 formatted start date string.
            end_date (str): ISO 8601 formatted end date string.

        Returns:
            list[dict]: A list of dictionaries containing booking details.

        Raises:
            ValueError: If the end date is before the start date.
        """
        self.logger.info(f"Received fetch bookings request: Start: {start_date}, End: {end_date}")

        start_time = start_date+"T00:00:00"
        end_time = end_date+"T23:59:59"

        if end_time < start_time:
            return "Error: End time must be after start time. Please try again."

        try:
            
            bookings = self.db.find({
            "$and": [
            {"start_time": {"$lte": end_time}},
            {"end_time": {"$gte": start_time}}
            ]})
            booked_records = []
            for booking in bookings:

                booked_records.append({
                    "_id": str(booking["_id"]),
                    "hall_id": booking["hall_id"],
                    "start_time": booking["start_time"],
                    "end_time": booking["end_time"],
                    "seats booked": booking["seats_booked"]
                })
            self.logger.info(f"Fetch bookings success: Start: {start_date}, End: {end_date}")
            return booked_records
        
        except Exception as e:
            self.logger.error(f'Fetch bookings failed,  Start: {start_date}, End: {end_date}: {e}')
            return []
        

    def cancel_booking(self, booking_id) -> str:
        """
        Cancel a booking by its booking ID.

        Args:
            booking_id (str): The ID of the booking to be canceled.

        Returns:
            str: A message indicating whether the cancellation was successful or an error occurred.
        """
        self.logger.info(f"Received cancellation request: Booking ID: {booking_id}")

        booking = self.db.find_one_and_delete({"_id": ObjectId(booking_id)})

        if booking:
            return f"Booking with ID {booking_id} has been cancelled successfully."
        else:
            return f"Booking with ID {booking_id} not found."


    def update_booking(self, booking_id, new_start_time, new_end_time, new_capacity) -> str:
        """
        Update the start and end times of an existing booking.

        Args:
            short_booking_id (str): The short ID of the booking to be updated.
            new_start_time (str): ISO 8601 formatted new start time string.
            new_end_time (str): ISO 8601 formatted new end time string.

        Returns:
            str: A message indicating whether the update was successful or an error occurred.
        """
        self.logger.info(f"Received update request: Booking ID: {booking_id}, New Start: {new_start_time}, New End: {new_end_time}")

        if not self.verify_time_range(new_start_time, new_end_time):
            return "Error: End time must be after start time. Please try again."
        
        # checking if the booking to be updated exists or not
        booking = self.db.find_one({'_id': ObjectId(booking_id)})

        if not booking:
            return f"Booking with ID {booking_id} not found."

        hall_id = booking['hall_id']
        old_start_time = booking['start_time']
        old_end_time = booking['end_time']

        lock_conflict = not (new_end_time < old_start_time or new_start_time > old_end_time)
        lock_aquired = False

        # aquire lock for the combined slot if old slot and new slot overlaps
        if lock_conflict:
            lock_start_time = min(old_start_time,new_start_time)
            lock_end_time = min(old_end_time,new_end_time)
            if self.lock_service.acquire_lock(hall_id, lock_start_time, lock_end_time):
                lock_aquired = True

        # else aquire lock only for the new slot
        elif(self.lock_service.acquire_lock(hall_id, old_start_time, old_end_time) and 
            self.lock_service.acquire_lock(hall_id, new_start_time, new_end_time)):
                lock_aquired = True

        if lock_aquired:
            try:
                query_to_find_conflicts = {
                "hall_id": hall_id,
                "_id": {"$ne": ObjectId(booking_id)},  # Exclude the booking with this ID
                "$and": [
                    {"start_time": {"$lt": new_end_time}},
                    {"end_time": {"$gt": new_start_time}}
                ]}
                # checking if no existing bookings are these for the new slot
                if not self.db.find_one(query_to_find_conflicts):

                    search_query = {'_id': ObjectId(booking_id)}
                    update_query = {'$set': {'start_time': new_start_time, 'end_time': new_end_time, 'seats_booked':new_capacity}}
                    result = self.db.update_one(search_query,update_query)
                    if result.modified_count > 0:
                        self.logger.info(f'Update success, Booking ID: {booking_id}, Start: {new_start_time}, End: {new_end_time}')
                        return f"Booking with ID {booking_id} has been updated successfully."
                    else:
                        self.logger.info(f"Update failed! Booking ID: {booking_id}, New Start: {new_start_time}, New End: {new_end_time}")
                        return f"Failed to update or booking with ID {booking_id} has same updates."

                else:
                    self.logger.info(f"Update failed, slot already booked: Booking ID: {booking_id}, New Start: {new_start_time}, New End: {new_end_time}")
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

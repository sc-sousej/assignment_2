from database.db_module import BookingDatabase
from models.booking import Booking
from utils.logger import setup_logger
from datetime import datetime
from models.halls import halls
from threading import Lock
import pymongo
import time


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
        Initialize the BookingController instance by setting up the database connection 
        and logger. Logs an error if the database connection fails.
        """
        self.db = BookingDatabase()
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
    

    def book_hall(self, hall_id, start_time, end_time) -> str:
        """
        Attempt to book a hall for the given time range. Handles concurrency using a lock.

        Args:
            hall_id (str): The ID of the hall to be booked.
            start_time (str): ISO 8601 formatted start time string.
            end_time (str): ISO 8601 formatted end time string.

        Returns:
            str: A message indicating whether the booking was successful or an error occurred.
        """
        self.logger.info(f"Received booking request: Hall {hall_id}, Start: {start_time}, End: {end_time}")

        if not self.verify_time_range(start_time, end_time):
            return "Error: End time must be after start time. Please try again."

        retry_interval = 0.01  # Retrying every 0.1 seconds
        max_wait_time = 5  
        waited_time = 0
        

        while waited_time < max_wait_time:
            try:
                with self.db.client.start_session() as session:
                    with session.start_transaction():
                        lock_acquired = False

                        try:
                            lock_result = self.db.get_lock(hall_id, session)
                            lock_acquired = lock_result.inserted_id == f'lock_{hall_id}'
                        except Exception:
                            # Lock is already acquired by another process
                            time.sleep(retry_interval)
                            waited_time += retry_interval
                            continue

                        if lock_acquired:
                            try:
                                available_halls = self.fetch_available_halls(start_time, end_time)
                                available_hall_ids = [hall['hall_id'] for hall in available_halls]

                                if hall_id in available_hall_ids:
                                    # print("hall available")
                                    booking = Booking(hall_id, start_time, end_time)
                                    booking_id = self.db.insert_hall_booking(booking.__dict__)
                                    self.logger.info(f"Booking successful for hall {hall_id}. Booking ID: {booking_id}")

                                    return f"Booking successful for hall {hall_id}. Booking ID: {booking_id}"
                                else:
                                    return "Hall is already booked for the given time slot."
                            finally:
                                # releasing hall lock
                                self.db.delete_lock(hall_id, session)
                        else:
                            self.logger.error(f"Lock aquired failed, Hall {hall_id}, Start: {start_time}, End: {end_time}")
            
            except pymongo.errors.OperationFailure as e:
                if 'errorLabels' in e.details and 'TransientTransactionError' in e.details['errorLabels']:
                    waited_time += retry_interval
                    # self.logger.warning(f"Transient error encountered. Retrying transaction ...")
                    time.sleep(retry_interval)
                else:
                    self.logger.error(f"Book hall failed! Hall {hall_id}, Start: {start_time}, End: {end_time}, Error: {e}")
                    return f"An error occurred while processing the booking: {e.details['errmsg']}"
            
        return "Another operation is currently modifying the database. Please try again later."

        
    def fetch_available_halls(self, start_time, end_time) -> list[dict]:
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
        bookings = self.db.fetch_available(start_time, end_time)

        booked_halls = [booking['hall_id'] for booking in bookings]
        available_halls = [{'hall_id': hall.name, 'capacity': hall.value} for hall in halls if hall.name not in booked_halls]
        
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

        start_time = datetime.fromisoformat(start_date)
        end_time = datetime.fromisoformat(end_date)

        if end_time < start_time:
            return "Error: End time must be after start time. Please try again."

        try:
            bookings = self.db.fetch_bookings(start_date, end_date)
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
        

    def cancel_booking(self, short_booking_id) -> str:
        """
        Cancel a booking by its booking ID.

        Args:
            short_booking_id (str): The short ID of the booking to be canceled.

        Returns:
            str: A message indicating whether the cancellation was successful or an error occurred.
        """
        self.logger.info(f"Received cancellation request: Booking ID: {short_booking_id}")

        try:
            # Using a transaction to ensure atomicity
            with self.db.client.start_session() as session:
                with session.start_transaction():
                    booking = self.db.find_booking(short_booking_id)
                    if not booking:
                        return f"Booking with ID {short_booking_id} not found."

                    result = self.db.delete_booking(short_booking_id)
                    if result.deleted_count > 0:
                        return f"Booking with ID {short_booking_id} has been cancelled successfully."
                    else:
                        return f"Booking with ID {short_booking_id} not found."
        except Exception as e:
            self.logger.error(f'Cancellation failed, Booking ID: {short_booking_id}: {e}')
            return "An error occurred while processing the cancellation."


    def update_booking(self, short_booking_id, new_start_time, new_end_time) -> str:
        """
        Update the start and end times of an existing booking.

        Args:
            short_booking_id (str): The short ID of the booking to be updated.
            new_start_time (str): ISO 8601 formatted new start time string.
            new_end_time (str): ISO 8601 formatted new end time string.

        Returns:
            str: A message indicating whether the update was successful or an error occurred.
        """
        
        self.logger.info(f"Received update request: Booking ID: {short_booking_id}, New Start: {new_start_time}, New End: {new_end_time}")

        if not self.verify_time_range(new_start_time, new_end_time):
            return "Error: End time must be after start time. Please try again."
        
        booking = self.db.find_booking(short_booking_id)

        if not booking:
            return f"Booking with ID {short_booking_id} not found."

        hall_id = booking['hall_id']
        booking_id = booking['booking_id']
        # old_start_time = booking['start_time']
        # old_end_time = booking['end_time']

        retry_interval = 0.01  # Retrying every 0.1 seconds
        max_wait_time = 5  
        waited_time = 0

        while waited_time < max_wait_time:
            try:
                with self.db.client.start_session() as session:
                    with session.start_transaction():
                        lock_acquired = False

                        try:
                            lock_result = self.db.get_lock(hall_id, session)
                            lock_acquired = lock_result.inserted_id == f'lock_{hall_id}'

                        except Exception:
                            # Lock is already acquired by another process
                            time.sleep(retry_interval)
                            waited_time += retry_interval
                            continue

                        if lock_acquired:
                            try:
                                conflicting_booking = self.db.find_conflicting_bookings(hall_id, booking_id, new_start_time, new_end_time)

                                if conflicting_booking is None:
                                    result = self.db.update_booking(booking_id, new_start_time, new_end_time)
                                    if result.modified_count > 0:
                                        self.logger.info(f'Update success, Booking ID: {booking_id}, Start: {new_start_time}, End: {new_end_time}')
                                        return f"Booking with ID {short_booking_id} has been updated successfully."
                                    else:
                                        return f"Failed to update booking with ID {short_booking_id}."
                                else:
                                    return "The new time slot is not available for the selected hall."

                            finally:
                                # releasing hall lock
                                self.db.delete_lock(hall_id, session)
                        else:
                            self.logger.error(f"error in update, Booking ID: {booking_id} ")

            except pymongo.errors.OperationFailure as e:
                if 'errorLabels' in e.details and 'TransientTransactionError' in e.details['errorLabels']:
                    waited_time += retry_interval
                    self.logger.warning(f"Transient error encountered. Retrying transaction ...")
                    time.sleep(retry_interval)
                else:
                    self.logger.error(f"Update failed! Booking ID: {booking_id}, Error: {e}")
                    return f"An error occurred while processing the update: {e.details['errmsg']}"
            

        return "Another operation is currently modifying the database. Please try again later."



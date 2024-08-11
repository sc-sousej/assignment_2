import pytest
from dotenv import load_dotenv
import os
import time
import threading
from utils.lock_manager import LockManager
from utils.lock_manager import Singleton
# from tests.zaid_lock import CustomLock



    
load_dotenv()
from services.booking_service import BookingService

def test_fetch_available_halls():
    service = BookingService()
    available_halls = service.fetch_available_halls("2024-08-01T10:00:00", "2024-08-01T12:00:00")
    print(available_halls)
    # assert "A" in available_halls  # Example assertion

def test_fetch_all_booked_halls():
    service = BookingService()
    all_booked_halls = service.fetch_all_booked_halls("2023-07-10", "2025-09-12")
    # assert "A" in available_halls  # Example assertion
    print("hello")
    

def test_book_hall():
    service = BookingService()
    print(service)
    time.sleep(3)
    result = service.book_hall("F", "2024-09-20T10:00:00", "2024-09-20T12:00:00","t-2")
    print(result)
    # assert result == "Booking successful"

def test_book_multiple_halls():
    service = BookingService()
    result = service.book_multiple_halls([
    {"hall_id": "B", "start_time": "2024-08-01T10:00:00", "end_time": "2024-08-01T12:00:00"},
    {"hall_id": "E", "start_time": "2024-08-01T13:00:00", "end_time": "2024-09-01T15:00:00"},
    {"hall_id": "C", "start_time": "2024-08-01T16:00:00", "end_time": "2024-08-01T18:00:00"}
    ])
    for booking_status in result:
        print(booking_status)

def test_delete_booking():
    service = BookingService()
    result = service.cancel_booking("1ac742")
    print(result)

def test_update_booking():
    service = BookingService()
    # service.update_booking()
    result = service.update_booking("9c86b0","2024-08-03T14:00:00","2025-08-04T16:00:00")
    print(result)



# if __name__ == '__main__':
    # test_update_booking()
    # test_delete_booking()
    # test_fetch_available_halls()
    # test_fetch_all_booked_halls()
    # test_book_multiple_halls()
    # test_book_hall()

# lock_service = LockManager()

# lock_service = Singleton.instance()
# print(lock_service)

# test_book_hall()

    # pytest.main()
num_threads = 10

# List to hold references to thread objects
threads = []

# Create and start threads
for i in range(num_threads):
    thread = threading.Thread(target=test_book_hall, name=f"Thread-{i+1}")
    threads.append(thread)
    thread.start()

# Wait for all threads to complete
for thread in threads:
    thread.join()

print("All threads have finished execution.")

import pytest
from dotenv import load_dotenv
import os
import time
import threading
from utils.lock_manager import LockManager
from datetime import datetime
# from utils.lock_manager import Singleton




load_dotenv()
from controller.booking_controller import BookingController


def test_fetch_available_halls():
    controller = BookingController()
    # print("call")
    available_halls = controller.fetch_available_halls("2024-08-01T10:00:00", "2024-08-01T12:00:00")
    print("ans=",available_halls)
    # assert "A" in available_halls  # Example assertion
    # {"available_halls":[{'hall_id':'A',"capacity":50},{'hall_id':'B',"capacity":100}]}


def test_fetch_all_booked_halls():
    controller = BookingController()
    all_booked_halls = controller.fetch_bookings("2024-08-01", "2024-08-30")
    # assert "A" in available_halls  # Example assertion
    print("hello",all_booked_halls)
    

def test_book_hall1():
    print("start 1")
    controller = BookingController()
    print(controller)
    # time.sleep(3)
    result = controller.book_hall("D", "2024-09-20T10:00:00", "2024-09-20T12:00:00")
    # controller.book_hall()
    print(result)
    # assert result == "Booking successful"

def test_book_hall2():
    print("start 1")

    controller = BookingController()
    print(controller)
    # time.sleep(3)
    result = controller.book_hall("D", "2024-09-20T09:00:00", "2024-09-20T12:00:00")
    # controller.book_hall()
    print(result)
    # assert result == "Booking successful"

def test_book_hall3():
    print("start 1")

    controller = BookingController()
    print(controller)
    # time.sleep(3)
    result = controller.book_hall("D", "2024-09-20T07:00:00", "2024-09-20T11:00:00")
    # controller.book_hall()
    print(result)
    # assert result == "Booking successful"

def test_book_multiple_halls():
    controller = BookingController()
    result = controller.book_multiple_halls([
    {"hall_id": "B", "start_time": "2024-08-01T10:00:00", "end_time": "2024-08-01T12:00:00"},
    {"hall_id": "E", "start_time": "2024-08-01T13:00:00", "end_time": "2024-09-01T15:00:00"},
    {"hall_id": "C", "start_time": "2024-08-01T16:00:00", "end_time": "2024-08-01T18:00:00"}
    ])
    for booking_status in result:
        print(booking_status)

def test_delete_booking():
    controller = BookingController()
    result = controller.cancel_booking("1ac742")
    print(result)

def test_update_booking():
    controller = BookingController()
    # controller.update_booking()
    result = controller.update_booking("9c86b0","2024-08-03T14:00:00","2025-08-04T16:00:00")
    print(result)



# if __name__ == '__main__':

# test_update_booking()
# test_delete_booking()
# test_fetch_available_halls()
# test_fetch_all_booked_halls()
# test_book_multiple_halls()
# test_book_hall()

# lock_controller = LockManager()

# lock_controller = Singleton.instance()
# print(lock_controller)

# test_book_hall()

    # pytest.main()
# num_threads = 10

# # List to hold references to thread objects
# threads = []

# # Create and start threads
# for i in range(num_threads):
#     thread = threading.Thread(target=test_book_hall1, name=f"Thread-{i+1}")
#     threads.append(thread)
#     thread.start()

# # Wait for all threads to complete
# for thread in threads:
#     thread.join()

# print("All threads have finished execution.")
# dateStr = input("enter date: ")
# print(datetime.fromisoformat(dateStr))
service = BookingController()
service.delete_all_bookings()


thread1 = threading.Thread(target=test_book_hall1)
thread2 = threading.Thread(target=test_book_hall2)
thread3 = threading.Thread(target=test_book_hall3)

# Start the threads
thread1.start()
thread2.start()
thread3.start()

# Wait for all threads to complete
thread1.join()
thread2.join()
thread3.join()
print("All threads have finished execution.")

import pytest
from dotenv import load_dotenv
import os
import time
import threading
# from utils.lock_manager import LockManager
from datetime import datetime
# from utils.lock_manager import Singleton




load_dotenv()
from controller.booking_controller import BookingController


def test_fetch_available_halls():
    controller = BookingController()
    # print("call")
    available_halls = controller.fetch_available_halls("2024-08-01T10:00:00", "2024-08-01T12:00:00",500)
    print("ans=",available_halls)
    # assert "A" in available_halls  # Example assertion
    # {"available_halls":[{'hall_id':'A',"capacity":50},{'hall_id':'B',"capacity":100}]}


def test_fetch_all_booked_halls():
    controller = BookingController()
    all_booked_halls = controller.fetch_bookings("2024-08-01", "2024-08-01")
    # assert "A" in available_halls  # Example assertion
    print("hello",all_booked_halls)
    

def test_book_hall1():
    # print("start 1")
    controller = BookingController()
    print(controller)
    # time.sleep(3)
    result = controller.book_hall("C", "2024-08-03T07:00:00", "2024-08-03T12:00:00",200)
    # controller.book_hall()
    print(result)
    # assert result == "Booking successful"

def test_book_hall2():
    # print("start 1")

    controller = BookingController()
    print(controller)
    # time.sleep(3)
    result = controller.book_hall("C", "2024-08-03T07:00:00", "2024-08-03T12:00:00",200)
    # controller.book_hall()
    print(result)
    # assert result == "Booking successful"

def test_book_hall3():
    # print("start 1")

    controller = BookingController()
    print(controller)
    # time.sleep(3)
    result = controller.book_hall("C", "2024-08-03T07:00:00", "2024-08-03T12:00:00",200)
    # controller.book_hall()
    print(result)
    # assert result == "Booking successful"

def test_book_multiple_halls():
    controller = BookingController()
    data = {"bookings":[
    {"hall_id": "A", "start_time": "2024-08-03T09:00:00", "end_time": "2024-08-03T12:00:00"},
    {"hall_id": "E", "start_time": "2024-08-01T13:00:00", "end_time": "2024-09-01T15:00:00"},
    {"hall_id": "C", "start_time": "2024-08-01T16:00:00", "end_time": "2024-08-01T18:00:00"}
    ]}
    for booking_data in data['bookings']:
                # self.book_hall_helper(booking_data)
        result = controller.book_hall(booking_data['hall_id'], booking_data['start_time'], booking_data['end_time'])
        print(result)

def test_delete_booking():
    controller = BookingController()
    result = controller.cancel_booking("09ef00")
    print(result)

def test_update_booking():
    controller = BookingController()
    # controller.update_booking()
    result = controller.update_booking("7fe8c4","2024-08-03T07:00:00","2024-08-03T12:00:00",200)
    print(result)

# service = BookingController()
# service.delete_all_bookings()


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


thread1 = threading.Thread(target=test_book_hall1)
thread2 = threading.Thread(target=test_update_booking)
# thread3 = threading.Thread(target=test_book_hall3)

# Start the threads
print("started 1")
thread1.start()
# time.sleep(7)
print("started 2")
thread2.start()
# # time.sleep(7)
# print("started 3")
# thread3.start()

# Wait for all threads to complete
thread1.join()
thread2.join()
# thread3.join()
print("All threads have finished execution.")

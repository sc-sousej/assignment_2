import unittest
import threading
import time
from controller.booking_controller import BookingController
 

class TestBookingConcurrency(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.controller = BookingController()
        cls.booking_ids = []  

    def test_01_concurrent_bookings_different_slots(self):
        def book_slot(hall_id, start_time, end_time, capacity):
            result = self.controller.book_hall(hall_id, start_time, end_time, capacity)
            # print(result)
            if "successful" in result:
                self.booking_ids.append(result[-24:])  # storing booking ID for later verification
                # print("appended",self.booking_ids)


        threads = []
        slots = [
            ("A", "2024-08-09T06:00", "2024-08-09T07:00",10),
            ("A", "2024-08-09T08:00", "2024-08-09T11:00",30),
            ("A", "2024-08-09T12:00", "2024-08-09T13:00",50),
            ("A", "2024-08-09T16:00", "2024-08-09T17:00",40),
        ]

        for hall_id, start_time, end_time, capacity in slots:
            thread = threading.Thread(target=book_slot, args=(hall_id, start_time, end_time, capacity))
            threads.append(thread)
            thread.start()

        for thread in threads:
            thread.join()

        self.assertEqual(len(self.booking_ids), 4)


    def test_02_concurrent_bookings_same_slot(self):

        def book_same_slot(hall_id, start_time, end_time, capacity):
            result = self.controller.book_hall(hall_id, start_time, end_time, capacity)
            if "successful" in result:
                self.booking_ids.append(result[-24:])  #  for later verification
                # print("appended",self.booking_ids)


        threads = []
        hall_id = "F"
        start_time = "2024-08-10T14:00"
        end_time = "2024-08-10T15:00"
        capacity = 300

        for _ in range(3):  # Three threads for the slot1
            thread = threading.Thread(target=book_same_slot, args=(hall_id, start_time, end_time, capacity))
            threads.append(thread)
            thread.start()

        hall_id_2 = "B"
        start_time_2 = "2024-08-10T14:30"
        end_time_2 = "2024-08-10T15:30"
        capacity2 = 80

        for _ in range(3):  # Three threads for slot 2
            thread = threading.Thread(target=book_same_slot, args=(hall_id_2, start_time_2, end_time_2, capacity2))
            threads.append(thread)
            thread.start()

        for thread in threads:
            thread.join()

        self.assertLessEqual(len(self.booking_ids), 6)  # Maximum 6 successful bookings


    def test_03_concurrent_updates(self):
        if len(self.booking_ids) < 2:
            self.fail("Not enough booking IDs to test updates.")

        booking_id_1 = self.booking_ids[0]
        booking_id_2 = self.booking_ids[1]
        new_start_time = "2024-09-09T16:00"
        new_end_time = "2024-09-09T17:00"
        capacity = 45

        successfull_update_count = 0

        def update_booking(booking_id, capacity):
            nonlocal successfull_update_count
            result = self.controller.update_booking(booking_id, new_start_time, new_end_time,capacity)
            print(result)
            if "successful" in result:
                successfull_update_count += 1
            return result

        threads = []
        for booking_id in [booking_id_1, booking_id_2]:
            thread = threading.Thread(target=update_booking, args=(booking_id,capacity))
            threads.append(thread)
            thread.start()

        for thread in threads:
            thread.join()

        # self.assertTrue(True)  # If no exceptions were raised, the updates were successful
        self.assertEqual(successfull_update_count,1)

if __name__ == "__main__":
    service = BookingController()
    service.delete_all_bookings()
    unittest.main()

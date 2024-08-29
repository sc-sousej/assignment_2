import unittest
from dotenv import load_dotenv
import os
from controller.booking_controller import BookingController


load_dotenv()

class TestBookingcontroller(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.controller = BookingController()
        cls.test_booking_id = ""

    def test_01_fetch_available_halls(self):
        available_halls = self.controller.fetch_available_halls("2024-08-01T10:00:00", "2024-08-01T11:00:00",500)
        hall_ids = [hall['hall_id'] for hall in available_halls]
        self.assertIn("F", hall_ids)

    def test_02_book_hall(self):
        result = self.controller.book_hall("F", "2024-07-01T10:00:00", "2024-08-02T12:00:00",800)
        self.__class__.test_booking_id = result[-24:]  # Store the booking ID for other tests
        self.assertIn("successful", result)

    def test_03_book_multiple_halls(self):
        data = {
            "bookings": [
                {"hall_id": "F", "start_time": "2024-08-03T13:00:00", "end_time": "2024-08-04T18:00:00","capacity":800},
                {"hall_id": "E", "start_time": "2024-09-01T13:00:00", "end_time": "2024-09-01T15:00:00","capacity":500},
                {"hall_id": "C", "start_time": "2024-08-01T16:00:00", "end_time": "2024-08-01T18:00:00","capacity":200}
            ]
        }
        for booking_data in data['bookings']:
            result = self.controller.book_hall(booking_data['hall_id'], booking_data['start_time'], booking_data['end_time'], booking_data['capacity'])
            self.assertIn("successful", result)

    def test_04_fetch_all_booked_halls(self):
        all_booked_halls = self.controller.fetch_bookings("2024-08-01", "2024-08-01")
        self.assertEqual(len(all_booked_halls), 2)

    def test_05_update_booking(self):
        result = self.controller.update_booking(self.__class__.test_booking_id, "2024-09-03T14:00:00", "2025-09-04T16:00:00",30)
        self.assertIn("updated successfully", result)

    def test_06_delete_booking(self):
        result = self.controller.cancel_booking(self.__class__.test_booking_id)
        self.assertIn("cancelled successfully", result)

if __name__ == '__main__':
    controller = BookingController()
    controller.delete_all_bookings()
    
    unittest.main()

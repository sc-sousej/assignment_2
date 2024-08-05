class Booking:
    def __init__(self, hall_id, start_time, end_time, booking_id=None):
        self.hall_id = hall_id
        self.start_time = start_time
        self.end_time = end_time
        self.booking_id = booking_id

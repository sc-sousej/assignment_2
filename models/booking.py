
class Booking:
    def __init__(self, hall_id, start_time, end_time, capacity):
        self.hall_id = hall_id
        self.start_time = start_time
        self.end_time = end_time
        self.seats_booked = capacity

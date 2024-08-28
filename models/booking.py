from bson import ObjectId

class Booking:
    def __init__(self, hall_id, start_time, end_time, capacity, booking_id=None):
        self.hall_id = hall_id
        self.start_time = start_time
        self.end_time = end_time
        self.booking_id = booking_id
        self.seats_booked = capacity

    # def set_booking_id(self, object_id):
    #     self.booking_id = str(object_id)[-6:]
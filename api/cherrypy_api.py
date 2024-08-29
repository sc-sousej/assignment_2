import cherrypy
from pymongo import MongoClient
from utils.logger import setup_logger
from controller.booking_controller import BookingController

class BookingAPI:

    def __init__(self):
        """
        Initialize the BookingAPI instance.

        Sets up the booking controller, MongoDB client, and logger.
        """
        self.booking_controller = BookingController()
        self.client = MongoClient("mongodb://localhost:27017/")
        self.logger = setup_logger("booking_api.log")

    @cherrypy.expose
    @cherrypy.tools.json_out()
    def home(self):
        print("welcome to seminar booking")
        return {"result":"seminar booking"}


    @cherrypy.expose
    @cherrypy.tools.json_out()
    @cherrypy.tools.json_in()
    def fetch_available(self):
        """
        Fetch available halls based on the provided criteria.

        Expects JSON input with keys: 'start_time', 'end_time', and 'capacity'.

        Returns:
            dict: A dictionary containing available halls or an error message.
        """
        try:
            data = cherrypy.request.json
            start_time = data.get("start_time")
            end_time = data.get("end_time")
            capacity = data.get("capacity")
            self.logger.info(f"Received fetch available hall request: Start: {start_time}, End: {end_time}, Capacity: {capacity}")
            available_halls = self.booking_controller.fetch_available_halls(start_time, end_time, capacity)
            return available_halls
        except Exception as e:
            self.logger.error("Invalid Input for fetch available request")

            return {"error":str(e)}

    @cherrypy.expose
    @cherrypy.tools.json_out()
    @cherrypy.tools.json_in()
    def book_hall(self):
        """
        Book a hall based on the provided criteria.

        Expects JSON input with keys: 'hall_id', 'start_time', 'end_time', and 'capacity'.

        Returns:
            dict: A dictionary containing the result of the booking operation or an error message.
        """
        try:
            data = cherrypy.request.json
            hall_id = data.get("hall_id")
            start_time = data.get("start_time")
            end_time = data.get("end_time")
            capacity = data.get("capacity")
            self.logger.info(f"Received booking request: Hall {hall_id}, Start: {start_time}, End: {end_time}, capcacity: {capacity}")
            result = self.booking_controller.book_hall(hall_id, start_time, end_time, capacity)
            return {"result": result}
        except:
            self.logger.error("Invalid Input for book hall request")
            return {"error": "Invalid Input"}
    

    @cherrypy.expose
    @cherrypy.tools.json_out()
    @cherrypy.tools.json_in()
    def book_multiple(self):
        """
        Book multiple halls based on the provided criteria.

        Expects JSON input with a 'bookings' key containing a list of booking details.

        Returns:
            dict: A dictionary containing the results of each booking operation or an error message.
        """
        try:
            data = cherrypy.request.json
            result = []
            for booking_data in data['bookings']:
                hall_id = booking_data.get("hall_id")
                start_time = booking_data.get("start_time")
                end_time = booking_data.get("end_time")
                capacity = booking_data.get("capacity")
                result.append(self.booking_controller.book_hall(hall_id, start_time, end_time, capacity))
            return {"result": result}
        except:
            self.logger.error("Invalid Input for book multiple halls request")

            return {"error": "Invalid Input"}

    @cherrypy.expose
    @cherrypy.tools.json_out()
    @cherrypy.tools.json_in()
    def fetch_bookings(self):
        """
        Fetch booking records based on the provided date range.

        Expects JSON input with keys: 'start_date' and 'end_date'.

        Returns:
            dict: A dictionary containing the bookings or an error message.
        """
        try:
            data = cherrypy.request.json
            start_date = data.get("start_date")
            end_date = data.get("end_date")
            self.logger.info(f"Received fetch bookings request: Start: {start_date}, End: {end_date}")
            bookings = self.booking_controller.fetch_bookings(start_date, end_date)
            return {"bookings": bookings}
        except:
            self.logger.error("Invalid Input for fetch bookings request")

            return {"error": "Invalid Input"}

    @cherrypy.expose
    @cherrypy.tools.json_out()
    @cherrypy.tools.json_in()
    def cancel_booking(self):
        """
        Cancel a booking based on the provided booking ID.

        Expects JSON input with a 'booking_id' key.

        Returns:
            dict: A dictionary containing the result of the cancellation operation or an error message.
        """
        try:
            data = cherrypy.request.json
            booking_id = data.get("booking_id")
            self.logger.info(f"Received cancellation request: Booking ID: {booking_id}")

            result = self.booking_controller.cancel_booking(booking_id)
            return {"result": result}
        except:
            self.logger.error("Invalid Input for cancellation request")
            return {"error": "Invalid Input"}

    @cherrypy.expose
    @cherrypy.tools.json_out()
    @cherrypy.tools.json_in()
    def update_booking(self):
        """
        Update a booking based on the provided booking ID and new details.

        Expects JSON input with keys: 'booking_id', 'new_start_time', 'new_end_time', and 'capacity'.

        Returns:
            dict: A dictionary containing the result of the update operation or an error message.
        """
        try:
            data = cherrypy.request.json
            booking_id = data.get("booking_id")
            new_start_time = data.get("new_start_time")
            new_end_time = data.get("new_end_time")
            capacity = data.get("capacity")
            self.logger.info(f'Received update request: Booking ID: {booking_id}, Start: {new_start_time}, End: {new_end_time}, Capacity: {capacity}')
            result = self.booking_controller.update_booking(booking_id, new_start_time, new_end_time,capacity)
            return {"result": result}
        except Exception as e:
            self.logger.error("Invalid Input for update booking request",e)
            return {"error": str(e)}

if __name__ == '__main__':
    cherrypy.config.update({
        'server.socket_host': '0.0.0.0',
        'server.socket_port': 8081,
    })
    cherrypy.quickstart(BookingAPI(), '/')

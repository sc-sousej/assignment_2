import cherrypy
from pymongo import MongoClient
from utils.logger import setup_logger
from controller.booking_controller import BookingController

class BookingAPI:

    def __init__(self):
        self.booking_controller = BookingController()
        self.client = MongoClient("mongodb://localhost:27017/")
        self.logger = setup_logger("booking_api.log")

    @cherrypy.expose
    @cherrypy.tools.json_out()
    # @cherrypy.tools.json_in()
    def home(self):
        print("welcome to seminar booking")
        return {"result":"seminar booking"}


    @cherrypy.expose
    @cherrypy.tools.json_out()
    @cherrypy.tools.json_in()
    def fetch_available(self):
        
        try:
            # hall_id = data.get("hall_id")
            data = cherrypy.request.json
            start_time = data.get("start_time")
            end_time = data.get("end_time")
            self.logger.info(f"Received fetch available hall request: Start: {start_time}, End: {end_time}")
            available_halls = self.booking_controller.fetch_available_halls(start_time, end_time)
            return available_halls
        except Exception as e:
            self.logger.error("Invalid Input for fetch available request")

            return {"error":str(e)}

    @cherrypy.expose
    @cherrypy.tools.json_out()
    @cherrypy.tools.json_in()
    def book_hall(self):
        try:
            data = cherrypy.request.json
            hall_id = data.get("hall_id")
            start_time = data.get("start_time")
            end_time = data.get("end_time")
            self.logger.info(f"Received booking request: Hall {hall_id}, Start: {start_time}, End: {end_time}")
            result = self.booking_controller.book_hall(hall_id, start_time, end_time)
            return {"result": result}
        except:
            self.logger.error("Invalid Input for book hall request")
            return {"error": "Invalid Input"}
    

    @cherrypy.expose
    @cherrypy.tools.json_out()
    @cherrypy.tools.json_in()
    def book_multiple(self):
        try:
            data = cherrypy.request.json
            result = []
            for booking_data in data['bookings']:
                hall_id = booking_data.get("hall_id")
                start_time = booking_data.get("start_time")
                end_time = booking_data.get("end_time")
                result.append(self.booking_controller.book_hall(hall_id, start_time, end_time))
            return {"result": result}
        except:
            self.logger.error("Invalid Input for book multiple halls request")

            return {"error": "Invalid Input"}

    @cherrypy.expose
    @cherrypy.tools.json_out()
    @cherrypy.tools.json_in()
    def fetch_bookings(self):
        
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
        
        try:
            data = cherrypy.request.json
            booking_id = data.get("booking_id")
            new_start_time = data.get("new_start_time")
            new_end_time = data.get("new_end_time")
            self.logger.info(f'Received update request: Booking ID: {booking_id}, Start: {new_start_time}, End: {new_end_time}')
            result = self.booking_controller.update_booking(booking_id, new_start_time, new_end_time)
            return {"result": result}
        except Exception as e:
            self.logger.error("Invalid Input for update booking request",e)
            return {"error": str(e)}

if __name__ == '__main__':
    cherrypy.config.update({
        'server.socket_host': '127.0.0.1',
        'server.socket_port': 8081,
    })
    cherrypy.quickstart(BookingAPI(), '/')

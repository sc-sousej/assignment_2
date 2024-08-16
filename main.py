import json
from datetime import datetime
from controller.booking_controller import BookingController


class BookingSystemCLI:

    def __init__(self):
        self.controller = BookingController()

    def verify_time_range(self,start, end):  

        start_time = datetime.fromisoformat(start)
        end_time = datetime.fromisoformat(end)

        if end_time > start_time:
            return True
        
        print("Error: End time must be after start time. Please try again.")
        return False
    
    def fetch_halls(self):
        print("Enter start and end time")
        print('eg- {"start_time":"2024-07-30T10:00:00","end_time":"2024-07-30T12:00:00"}: ')
        data = input("Enter JSON string: ").strip()
        try:
            data = json.loads(data)
            # if self.verify_time_range(data['start_time'], data['end_time']):
            available_halls = self.controller.fetch_available_halls(data['start_time'], data['end_time'])
            print("Available halls:", available_halls)
        except:
            print("enter data in correct form")


    def book_hall(self):
        print("enter hall_id, start time and end time")
        print('eg- {"hall_id":"B","start_time":"2024-07-30T10:00:00","end_time":"2024-07-30T12:00:00"}')
        data = input("Enter data as JSON string: ").strip()
        try:
            data = json.loads(data)
            # self.book_hall_helper(data)
            result = self.controller.book_hall(data['hall_id'], data['start_time'], data['end_time'])
            print(result)
        except:
            print("enter data in correct form")
        
        

    def view_bookings(self):

        print("enter start date and end date")
        print('eg- {"start_date": "2024-08-01", "end_date": "2024-08-02"}')
        data = input("Enter data as JSON string: ").strip()
        try:
            data = json.loads(data)
            result = self.controller.fetch_all_booked_halls(data['start_date'], data['end_date'])
            print(result)
                           
        except:
            print("enter data in correct form")

    def book_multiple_halls(self):

        print("enter hall_id, start time and end time for each booking")
        print('''eg- {"bookings":[
        {"hall_id": "A", "start_time": "2024-08-01T10:00:00", "end_time": "2024-08-01T12:00:00"},
        {"hall_id": "C", "start_time": "2024-08-01T16:00:00", "end_time": "2024-08-01T18:00:00"}
        ]}''')
        data = input("Enter data as JSON string: ")
        try:
            data = json.loads(data)
            for booking_data in data['bookings']:
                # self.book_hall_helper(booking_data)
                result = self.controller.book_hall(booking_data['hall_id'], booking_data['start_time'], booking_data['end_time'])
                # print(result)
        except:
            print("enter data in correct form")


    def cancel_booking(self):
        print('Enter the booking id as JSON string eg- {"booking_id": "abcdef"}: ')
        data = input()
        try:
            data = json.loads(data)
            result = self.controller.cancel_booking(data['booking_id'])
            print(result)
        except:
            print("enter data in correct form")

    def update_booking(self):
        print('Enter the booking id, new start and end time: ')
        print('''eg-{
        "booking_id": "abcdef",
        "new_start_time": "2024-08-01T14:00:00",
        "new_end_time": "2024-08-01T16:00:00"
        }''')
        data = input("enter data as JSON string: ").strip()

        try:
            data = json.loads(data)
            # if self.verify_time_range(data['new_start_time'], data['new_end_time']):
            result = self.controller.update_booking(data['booking_id'], data['new_start_time'], data['new_end_time'])
            print(result)
        except:
            print("enter data in correct form")

    def run(self):
        while True:
            user_input = input("Enter command (fetch, book, view, book_multiple cancel, update, exit): ").strip()
            if user_input == 'exit':
                break

            if user_input == 'fetch':
                self.fetch_halls()

            elif user_input == 'book':
                self.book_hall()

            elif user_input == 'view':
                self.view_bookings()

            elif user_input == 'book_multiple':
                self.book_multiple_halls()
            
            elif user_input == 'cancel':
                self.cancel_booking()

            elif user_input == 'update':
                self.update_booking()

    

if __name__ == '__main__':
    cli = BookingSystemCLI()
    cli.run()


import json
from datetime import datetime
from controller.booking_controller import BookingController


class BookingSystemCLI:

    def __init__(self):
        self.controller = BookingController()

    
    def fetch_halls(self):
        """
        Prompt the user to input start time, end time, and capacity to fetch available halls.

        This function expects a JSON string input from the user and fetches available halls based on the provided criteria.
        """
        print("Enter start and end time")
        print('eg- {"start_time":"2024-07-30T10:00:00","end_time":"2024-07-30T12:00:00","capacity":50}: ')
        data = input("Enter JSON string: ").strip()
        try:
            data = json.loads(data)
            available_halls = self.controller.fetch_available_halls(data['start_time'], data['end_time'], data['capacity'])
            print("Available halls:", available_halls)
        except:
            print("enter data in correct form")


    def book_hall(self):
        """
        Prompt the user to input hall ID, start time, end time, and capacity to book a hall.

        This function expects a JSON string input from the user and attempts to book the specified hall.
        """
        print("enter hall_id, start time and end time")
        print('eg- {"hall_id":"B","start_time":"2024-07-30T10:00:00","end_time":"2024-07-30T12:00:00","capacity":50}')
        data = input("Enter data as JSON string: ").strip()
        try:
            data = json.loads(data)
            result = self.controller.book_hall(data['hall_id'], data['start_time'], data['end_time'], data['capacity'])
            print(result)
        except:
            print("enter data in correct form")
        

    def view_bookings(self):
        """
        Prompt the user to input a date range to view bookings.

        This function expects a JSON string input from the user and fetches bookings within the specified date range.
        """
        print("enter start date and end date")
        print('eg- {"start_date": "2024-08-01", "end_date": "2024-08-02"}')
        data = input("Enter data as JSON string: ").strip()
        try:
            data = json.loads(data)
            result = self.controller.fetch_bookings(data['start_date'], data['end_date'])
            for item in result:
                print(item)
                           
        except:
            print("enter data in correct form")


    def book_multiple_halls(self):
        """
        Prompt the user to input multiple booking requests.

        This function expects a JSON string input containing a list of bookings and attempts to book multiple halls based on the provided data.
        """
        print("enter hall_id, start time and end time for each booking")
        print('''eg- {"bookings":[
        {"hall_id": "A", "start_time": "2024-08-01T10:00:00", "end_time": "2024-08-01T12:00:00","capacity":50},
        {"hall_id": "C", "start_time": "2024-08-01T16:00:00", "end_time": "2024-08-01T18:00:00","capacity":50}
        ]}''')
        data = input("Enter data as JSON string: ")
        try:
            data = json.loads(data)
            for booking_data in data['bookings']:
                result = self.controller.book_hall(booking_data['hall_id'], booking_data['start_time'], booking_data['end_time'], booking_data['capacity'])
                print(result)
        except Exception as e:
            print("enter data in correct form ",e)


    def cancel_booking(self):
        """
        Prompt the user to input a booking ID to cancel the booking.

        This function expects a JSON string input from the user and attempts to cancel the specified booking.
        """
        print('Enter the booking id as JSON string eg- {"booking_id": "abcdef1234"}: ')
        data = input()
        try:
            data = json.loads(data)
            result = self.controller.cancel_booking(data['booking_id'])
            print(result)
        except:
            print("enter data in correct form")


    def update_booking(self):
        """
        Prompt the user to input a booking ID, new start time, new end time, and capacity to update an existing booking.

        This function expects a JSON string input from the user and attempts to update the specified booking.
        """
        print('Enter the booking id, new start and end time: ')
        print('''eg-{
        "booking_id": "abcdef1234",
        "new_start_time": "2024-08-01T14:00:00",
        "new_end_time": "2024-08-01T16:00:00",
        "capacity":50
        }''')
        data = input("enter data as JSON string: ").strip()

        try:
            data = json.loads(data)
            result = self.controller.update_booking(data['booking_id'], data['new_start_time'], data['new_end_time'], data['capacity'])
            print(result)
        except:
            print("enter data in correct form")


    def run(self):
        """
        Run the CLI interface to handle user commands.

        This function continuously prompts the user for commands and calls the corresponding methods until 'exit' is entered.
        """
        while True:
            user_input = input("Enter command (fetch, book, view, book_multiple, cancel, update, exit): ").strip()
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


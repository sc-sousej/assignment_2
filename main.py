import json
from services.booking_service import BookingService

def main():
    service = BookingService()

    while True:
        user_input = input("Enter command (fetch, book, view, book_multiple cancel, update, exit): ").strip()
        if user_input == 'exit':
            break


        if user_input == 'fetch':
            print("Enter start and end time")
            print('eg- {"start_time":"2024-07-30T10:00:00","end_time":"2024-07-30T12:00:00"}: ')
            data = input("Enter JSON string: ").strip()
            data = json.loads(data)
            available_halls = service.fetch_available_halls(data['start_time'], data['end_time'])
            print("Available halls:", available_halls)

        elif user_input == 'book':
            print("enter hall_id, start time and end time")
            print('eg- {"hall_id":"B","start_time":"2024-07-30T10:00:00","end_time":"2024-07-30T12:00:00"}')
            data = input("Enter data as JSON string: ").strip()
            data = json.loads(data)
            result = service.book_hall(data['hall_id'], data['start_time'], data['end_time'])
            print(result)

        elif user_input == 'view':
            print("enter start date and end date")
            print('eg- {"start_date": "2024-08-01", "end_date": "2024-08-02"}')
            data = input("Enter data as JSON string: ").strip()
            data = json.loads(data)
            result = service.fetch_all_booked_halls(data['start_date'], data['end_date'])
            print(result)

        elif user_input == 'book_multiple':
            print("enter hall_id, start time and end time for each booking")
            print('''eg- [
            {"hall_id": "A", "start_time": "2024-08-01T10:00:00", "end_time": "2024-08-01T12:00:00"},
            {"hall_id": "C", "start_time": "2024-08-01T16:00:00", "end_time": "2024-08-01T18:00:00"}
            ]''')
            data = input("Enter data as JSON string: ").strip()

            bookings = json.loads(data)
            results = service.book_multiple_halls(bookings)
            for result in results:
                print(f"Hall ID {result['hall_id']}: {result['result']}")

        # Implement other commands similarly
        # {"start_time":"2024-07-30T10:00:00","end_time":"2024-07-30T12:00:00"}
        # book
        # {"hall_id":"B","start_time":"2024-07-30T10:00:00","end_time":"2024-07-30T12:00:00"}   
        # view all
        # {"start_date": "2024-08-01", "end_date": "2024-08-02"}

if __name__ == '__main__':
    main()

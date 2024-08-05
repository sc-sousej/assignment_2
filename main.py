import json
from services.booking_service import BookingService

def main():
    service = BookingService()

    while True:
        user_input = input("Enter command (fetch, book, view, cancel, update, exit): ").strip()
        if user_input == 'exit':
            break

        data = input("Enter data as JSON string: ").strip()
        data = json.loads(data)

        if user_input == 'fetch':
            available_halls = service.fetch_available_halls(data['start_time'], data['end_time'])
            print("Available halls:", available_halls)
        elif user_input == 'book':
            result = service.book_hall(data['hall_id'], data['start_time'], data['end_time'])
            print(result)
        # Implement other commands similarly

if __name__ == '__main__':
    main()

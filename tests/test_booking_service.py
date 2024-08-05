import pytest
from dotenv import load_dotenv
import os

load_dotenv()
from services.booking_service import BookingService

def test_fetch_available_halls():
    service = BookingService()
    available_halls = service.fetch_available_halls("2024-07-30T10:00:00", "2024-07-30T12:00:00")
    assert "A" in available_halls  # Example assertion

def test_book_hall():
    service = BookingService()
    result = service.book_hall("A", "2024-07-30T10:00:00", "2024-07-30T12:00:00")
    assert result == "Booking successful"

if __name__ == '__main__':
    pytest.main()

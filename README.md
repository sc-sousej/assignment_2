# Hall Booking System
Overview

The Seminar Hall Booking System is an application that allows users to book seminar halls, update bookings, cancel bookings, and retrieve booking records. It supports concurrency control to handle simultaneous booking requests and provides an optional RESTful API using CherryPy.

Features

    Fetch available halls for a specific time slot.
    Book a seminar hall.
    Fetch all bookings within a date range.
    Book multiple halls in a single request.
    Cancel a booking.
    Update an existing booking.

    Concurrency control using locks.
    Logging to track system events.
    Unit tests to verify functionality and concurrency.
    RESTful API integration using CherryPy.



Installation
1. Clone the Repository

bash

git clone https://github.com/yourusername/seminar-hall-booking.git
cd seminar-hall-booking

2. Set Up a Virtual Environment (Optional)

bash

python3 -m venv venv
source venv/bin/activate  # On Windows use `venv\Scripts\activate`

3. Install Dependencies

bash

pip install -r requirements.txt

4. Setup Mongo



Running the Application

You can run the booking system directly from the terminal. The application takes JSON strings as input for various operations.

Example:

bash

python main.py

Running the RESTful API

To enable the RESTful API, ensure that CherryPy is installed, and then run:

bash

python api/cherrypy_api.py 

The API will be accessible at http://localhost:8081.


Running Tests
1. Install Testing Dependencies

Ensure unittest and any other required libraries are installed. They should be included in requirements.txt.
2. Run Unit Tests

bash

python sequential_unittest.py
python multithreading_unittest.py


Logging

The system also supports logging to files. 

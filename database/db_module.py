from pymongo import MongoClient,ReturnDocument
from datetime import datetime, timezone


class BookingDatabase:
    _instance = None

    def __new__(cls):
        """
        Ensure that only one instance of the BookingDatabase class exists.
        
        Returns:
            BookingDatabase: The singleton instance of the BookingDatabase class.
        """
        if cls._instance is None:
            cls._instance = super(BookingDatabase, cls).__new__(cls)
            cls._instance.client = MongoClient('mongodb://localhost:27017/')
            cls._instance.db = cls._instance.client['seminar_hall_booking']
            cls._instance.bookings = cls._instance.db.bookings
        return cls._instance

    def delete_database(self) -> dict:
        """
        Deletes all documents in the bookings collection.

        Returns:
            dict: A dictionary containing the deletion result details.
        """
        return self.bookings.delete_many({})


    def update_one(self, query, update, upsert = False):
        return self.bookings.update_one(query, update, upsert = upsert)


    def insert_hall_booking_old(self,data) -> str:
        """
        Inserts a new booking into the bookings collection and generates a booking ID.

        Args:
            data (dict): The booking data to insert.

        Returns:
            str: The generated booking ID.
        """
        result = self.bookings.insert_one(data)
        booking_id = str(result.inserted_id)[-6:]
        self.bookings.update_one({'_id': result.inserted_id}, {'$set': {'booking_id': booking_id}})
        return booking_id

    def fetch_available(self,start_time, end_time):
        """
        Fetches available bookings that are in given time range or clashes with this tmie range.

        Args:
            start_time (str): The start time of the desired booking.
            end_time (str): The end time of the desired booking.

        Returns:
            pymongo.cursor.Cursor: A cursor to the documents that match the query.
        """
        return self.bookings.find({
            "$or": [
                {"start_time": {"$lte": end_time, "$gte": start_time}},
                {"end_time": {"$lte": end_time, "$gte": start_time}}
            ]})

    def fetch_bookings(self,start_date, end_date):
        """
        Fetches all bookings within the given date range.

        Args:
            start_date (str): The start date in the format YYYY-MM-DD.
            end_date (str): The end date in the format YYYY-MM-DD.

        Returns:
            pymongo.cursor.Cursor: A cursor to the documents that match the query.
        """
        start_date_obj = start_date+"T00:00:00"
        end_date_obj = end_date+"T23:59:59"
        return self.bookings.find({
            "$and": [
            {"start_time": {"$lte": end_date_obj}},
            {"end_time": {"$gte": start_date_obj}}
            ]})
    
    def find_booking(self,booking_id) -> dict:
        """
        Finds a booking by its booking ID.

        Args:
            booking_id (str): The booking ID to search for.

        Returns:
            dict: The document corresponding to the booking ID, or None if not found.
        """
        return self.bookings.find_one({'booking_id': booking_id})
    
    def delete_booking(self, booking_id) -> dict:
        """
        Deletes a booking by its booking ID.

        Args:
            booking_id (str): The booking ID of the booking to delete.

        Returns:
            dict: A dictionary containing the deletion result details.
        """
        return self.bookings.delete_one({'booking_id': booking_id})
    
    def find_conflicting_bookings(self,hall_id, booking_id,new_start_time, new_end_time) -> dict:
        """
        Finds conflicting bookings for a given hall and time range, excluding a specific booking.

        Args:
            hall_id (str): The ID of the hall.
            booking_id (str): The ID of the booking to exclude.
            new_start_time (str): The new start time of the booking.
            new_end_time (str): The new end time of the booking.

        Returns:
            dict: The document of the conflicting booking, or None if no conflict is found.
        """
        query = {
                "hall_id": hall_id,
                "booking_id": {"$ne": booking_id},  # Excluding the provided booking_id
                "$or": [
                    {"start_time": {"$lt": new_end_time}, "end_time": {"$gt": new_start_time}}
                ]}
        return self.bookings.find_one(query)
    
    def update_booking(self, booking_id, new_start_time, new_end_time) -> dict:
        """
        Updates the time range of a booking.

        Args:
            booking_id (str): The ID of the booking to update.
            new_start_time (str): The new start time of the booking.
            new_end_time (str): The new end time of the booking.

        Returns:
            dict: A dictionary containing the update result details.
        """
        return self.bookings.update_one(
                {'booking_id': booking_id},
                {'$set': {'start_time': new_start_time, 'end_time': new_end_time}}
            )

    def update_2(self,booking_id, new_start_time, new_end_time, hall_id):
        # return self.bookings.aggregate(pipeline)
        result = self.bookings.update_one(
        {"booking_id": booking_id},
        [
            {
                "$set": {
                    "start_time": 
                    {
                        "$cond": {
                            "if": {
                                "$eq": [
                                    {
                                        "$size": {
                                            "$filter": {
                                            "input": {
                                                "$cond": {
                                                "if": {
                                                    "$eq": [
                                                    {
                                                        "$type": "$$ROOT"
                                                    },
                                                    "array"
                                                    ]
                                                },
                                                "then": "$$ROOT",
                                                "else": [
                                                    "$$ROOT"
                                                ],
                                                
                                                }
                                            },  # Using the current document as input
                                            "as": "conflict",
                                            "cond": {
                                                "$and": [
                                                    {"$ne": ["$$conflict.booking_id", booking_id]},
                                                    {"$eq": ["$$conflict.hall_id", hall_id]},
                                                    {"$and": [
                                                        {"$lt":["$$conflict.start_time", new_end_time]},
                                                        {"$gt":["$$conflict.end_time", new_start_time]}

                                                    ]}
                                                ]
                                            }
                                        }
                                        }
                                    },
                                    0
                                ]
                            },
                            "then": new_start_time,
                            "else": "$start_time"  # Keep the original start time if conflicts are found
                        }
                    }
                    ,
                    "end_time":
                    {
                        "$cond": {
                            "if": {
                                "$eq": [
                                    {
                                        "$size": {
                                            "$filter": {
                                            "input": {
                                                "$cond": {
                                                "if": {
                                                    "$eq": [
                                                    {
                                                        "$type": "$$ROOT"
                                                    },
                                                    "array"
                                                    ]
                                                },
                                                "then": "$$ROOT",
                                                "else": [
                                                    "$$ROOT"
                                                ],
                                                
                                                }
                                            },  # Using the current document as input
                                            "as": "conflict",
                                            "cond": {
                                                "$and": [
                                                    {"$ne": ["$$conflict.booking_id", booking_id]},
                                                    {"$eq": ["$$conflict.hall_id", hall_id]},
                                                    {"$and": [
                                                        {"$lt":["$$conflict.start_time", new_end_time]},
                                                        {"$gt":["$$conflict.end_time", new_start_time]}

                                                    ]}
                                                ]
                                            }
                                        }
                                        }
                                    },
                                    0
                                ]
                            },
                            "then": new_end_time,
                            "else": "$end_time"  # Keep the original end time if conflicts are found
                        }
                    }
                }
            }
        ]
    ) 
        

        
        return result

    def find_one_and_update(self,booking_id, search_query, update_query,hall_id):
        return self.bookings.find_one_and_update(
        {'booking_id': booking_id, "$and": [{"hall_id": hall_id}, {"$or": search_query['$and'][1]['$or']}]},
        update_query,
        upsert=False,  # We don't want to insert if the booking_id doesn't exist
        return_document=False  # Returns the original document before update
    )

    def get_lock(self, hall_id, session) -> dict:
        """
        Acquires a lock for a specific hall during a session.

        Args:
            hall_id (str): The ID of the hall to lock.
            session: The MongoDB session in which to perform the operation.

        Returns:
            dict: The result of the insert operation.
        """
        return self.db['locks'].insert_one(
            {'_id': f'lock_{hall_id}', 'locked_at': datetime.now(timezone.utc)},
            session=session)
    
    def delete_lock(self, hall_id, session) -> dict:
        """
        Releases the lock for a specific hall during a session.

        Args:
            hall_id (str): The ID of the hall to unlock.
            session: The MongoDB session in which to perform the operation.

        Returns:
            dict: The result of the delete operation.
        """
        self.db['locks'].delete_one({'_id': f'lock_{hall_id}'}, session=session)




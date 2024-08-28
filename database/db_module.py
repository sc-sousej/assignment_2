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

    def find(self, query):
        return self.bookings.find(query)

    def find_one(self,query):
        return self.bookings.find_one(query)

    def update_one(self, query, update, upsert = False):
        return self.bookings.update_one(query, update, upsert = upsert)


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


    
    def find_one_and_delete(self, query) -> dict:
       
        return self.bookings.find_one_and_delete(query)
    


    


    def update_2(self,booking_id, new_start_time, new_end_time, hall_id):
        # return self.bookings.aggregate(pipeline)
        pipeline = [
            {
                "$match": {
                    "hall_id": hall_id,
                    "$or": [
                        {"start_time": {"$lt": new_end_time}, "end_time": {"$gt": new_start_time}},
                        {"booking_id": booking_id}
                    ]
                }
            },
            {
                "$count": "total_docs"
            },
            {
                "$project": {
                    "booking_id_found": booking_id,
                    "total_docs": 1
                }
            }
        ]

        # Run the aggregation pipeline
        # result = list(self.bookings.aggregate(pipeline))
        
        query = {
                    "hall_id": hall_id,
                    "$or": [
                        {"start_time": {"$lt": new_end_time}, "end_time": {"$gt": new_start_time}},
                        {"booking_id": booking_id}
                    ]
                }
        
        result = self.bookings.update_one(
            {
                "$expr": {
                    "$and": [
                        {"$eq": [{"$size": {"$filter": {"input": pipeline, "as": "docs", "cond": {"$eq": ["$$docs.total_docs", 1]}}}}, 1]},
                        {"$eq": ["$$docs.booking_id_found", True]}
                    ]
                }
            },
            {"$set": {"start_time": new_start_time, "end_time": new_end_time}}
        )
        # print("r=",[r for r in result])
        # result = self.bookings.update_one(query,
        #     {
        #         "$set": {"start_time": new_start_time, "end_time": new_end_time}
        #     }
        # )

        
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




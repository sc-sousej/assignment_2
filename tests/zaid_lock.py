import threading
from datetime import datetime

class CustomLock:
    def __init__(self):
        self.lock = threading.Lock()
        self.locked_ranges = []  # List of tuples: (hall_id, start_time, end_time, operation_type, booking_id)
        self.update_and_cancel_locks = {}  # Dictionary to keep track of booking IDs

    def acquire_lock(self, hall_id, start_time, end_time, operation_type, booking_id=None):
        with self.lock:
            # Check for conflicts with datetime ranges and hall IDs
            for (existing_hall_id, existing_start, existing_end, existing_operation, existing_booking_id) in self.locked_ranges:
                if existing_hall_id == hall_id and not (end_time <= existing_start or start_time >= existing_end):
                    if existing_operation in ['booking', 'fetch_available_halls'] and operation_type in ['booking', 'fetch_available_halls']:
                        # Conflict detected for booking or fetch operation
                        return False
                    if existing_operation == 'update' and operation_type in ['update', 'cancel']:
                        # Allow update or cancel if booking IDs are different
                        if booking_id and existing_booking_id and booking_id != existing_booking_id:
                            continue
                        return False

            # No conflicts detected, add to locked_ranges
            self.locked_ranges.append((hall_id, start_time, end_time, operation_type, booking_id))
            if operation_type in ['update', 'cancel']:
                if booking_id:
                    self.update_and_cancel_locks[booking_id] = (start_time, end_time)
            return True

    def release_lock(self, hall_id, start_time, end_time, operation_type, booking_id=None):
        with self.lock:
            self.locked_ranges = [item for item in self.locked_ranges if not (
                item[0] == hall_id and item[1] == start_time and item[2] == end_time and item[3] == operation_type and item[4] == booking_id
            )]
            if operation_type in ['update', 'cancel']:
                if booking_id in self.update_and_cancel_locks:
                    del self.update_and_cancel_locks[booking_id]

    def is_locked(self, hall_id, start_time, end_time, operation_type, booking_id=None):
        with self.lock:
            for (existing_hall_id, existing_start, existing_end, existing_operation, existing_booking_id) in self.locked_ranges:
                if existing_hall_id == hall_id and not (end_time <= existing_start or start_time >= existing_end):
                    if existing_operation in ['booking', 'fetch_available_halls'] and operation_type in ['booking', 'fetch_available_halls']:
                        return True
                    if existing_operation == 'update' and operation_type in ['update', 'cancel']:
                        if booking_id and existing_booking_id and booking_id != existing_booking_id:
                            continue
                        return True
            return False
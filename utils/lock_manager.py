from threading import Lock, Condition
from collections import defaultdict, deque
from datetime import datetime
from utils.logger import setup_logger
import time


class LockManager:

    _instance = None
    _lock = Lock()
    

    def __new__(cls, *args, **kwargs):
        """
        Ensure a single instance of LockManager (Singleton pattern).

        Args:
            *args: Variable length argument list.
            **kwargs: Arbitrary keyword arguments.

        Returns:
            LockManager: The single instance of the LockManager class.
        """
        with cls._lock:
            if cls._instance is None:
                cls._instance = super().__new__(cls)
                cls._instance._initialize()
        return cls._instance
    
    
    def _initialize(self):
        """
        Initialize the LockManager instance.

        Sets up the data structures for managing locks and conditions, and initializes the logger.
        """
        self.locks = defaultdict(dict)
        self.conditions = defaultdict(dict)
        self.logger = setup_logger("lock_manager.log")


    def _is_time_conflict(self, existing_start, existing_end, new_start, new_end) -> bool:
        """
        Determine if there is a time conflict between two time ranges.

        Args:
            existing_start (datetime): The start time of the existing booking.
            existing_end (datetime): The end time of the existing booking.
            new_start (datetime): The start time of the new booking.
            new_end (datetime): The end time of the new booking.

        Returns:
            bool: True if there is a time conflict, False otherwise.
        """
        return not (new_end <= existing_start or new_start >= existing_end)

        
    def acquire_lock(self, hall_id, start_time, end_time, timeout=5) -> bool:
        """
        Attempt to acquire a lock for a specific time slot for a hall.

        Args:
            hall_id (str): The ID of the hall for which the lock is being requested.
            start_time (str): The start time of the booking (ISO format).
            end_time (str): The end time of the booking (ISO format).
            timeout (int, optional): The maximum time (in seconds) to wait for acquiring the lock. Default is 10.

        Returns:
            bool: True if the lock was successfully acquired, False otherwise.
        """
        retry_interval = 0.0001  
        waited_time = 0

        self.logger.info(f'Lock request received, Hall id: {hall_id}, start: {start_time}, end: {end_time}')
        start_time = datetime.fromisoformat(start_time)
        end_time = datetime.fromisoformat(end_time)

        if hall_id not in self.locks:
            self.locks[hall_id] = {}
            self.conditions[hall_id] = {}

        # Ensure condition variable for the time slot
        if (start_time, end_time) not in self.conditions[hall_id]:
            self.conditions[hall_id][(start_time, end_time)] = Condition()

        with self.conditions[hall_id][(start_time, end_time)]:
            while waited_time < timeout:
                try:
                    # Checking for any existing locks on the given time slot
                    conflict = False
                    for (existing_start, existing_end) in self.locks[hall_id]:
                        if self._is_time_conflict(existing_start, existing_end, start_time, end_time):
                            conflict = True
                            time.sleep(retry_interval)
                            waited_time += retry_interval
                            continue

                    if not conflict:
                        # No existing locks, acquiring lock
                        self.locks[hall_id][(start_time, end_time)] = Lock()
                        res = self.locks[hall_id][(start_time, end_time)].acquire()
                        self.logger.info(f'Lock Aquired, Hall id: {hall_id}, start: {start_time}, end: {end_time}')
                        return True
                    
                except Exception as e:
                    # some error, wait and retry to aquire lock
                    conflict = True
                    time.sleep(retry_interval)
                    waited_time += retry_interval
                    continue

            self.logger.error(f"lock aquire failed Hall id: {hall_id}, start: {start_time}, end: {end_time}")
                            

    def release_lock(self, hall_id, start_time, end_time):
        """
        Release a previously acquired lock for a specific time slot for a hall.

        Args:
            hall_id (str): The ID of the hall for which the lock is being released.
            start_time (str): The start time of the booking (ISO format).
            end_time (str): The end time of the booking (ISO format).

        Returns:
            None
        """
        start_time = datetime.fromisoformat(start_time)
        end_time = datetime.fromisoformat(end_time)

        if hall_id in self.locks and (start_time, end_time) in self.locks[hall_id]:
            self.locks[hall_id][(start_time, end_time)].release()
            self.logger.info(f'Lock Released, Hall id: {hall_id}, start: {start_time}, end: {end_time}')
            # lock released
            del self.locks[hall_id][(start_time, end_time)]

               
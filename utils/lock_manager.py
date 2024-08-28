from threading import Lock, Condition
from collections import defaultdict, deque
from datetime import datetime
from utils.logger import setup_logger
import time


class LockManager:

    _instance = None
    _lock = Lock()

    

    def __new__(cls, *args, **kwargs):
        with cls._lock:
            if cls._instance is None:
                # print("NONE INST")
                cls._instance = super().__new__(cls)
                cls._instance._initialize()
        return cls._instance
    
    def _initialize(self):
        self.locks = defaultdict(dict)
        self.conditions = defaultdict(dict)
        self.logger = setup_logger("lock_manager.log")


    def _is_time_conflict(self, existing_start, existing_end, new_start, new_end):
        return not (new_end <= existing_start or new_start >= existing_end)

    def acquire_lock(self, hall_id, start_time, end_time, timeout=10):
        # with self._lock:

        retry_interval = 0.01  # Retrying every 0.1 seconds
        max_wait_time = 5  
        waited_time = 0

        # while waited_time < max_wait_time:

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
            while waited_time < max_wait_time:
                # Check for any time conflicts
                conflict = False
                # print("hall-id-",self.locks[hall_id])
                for (existing_start, existing_end) in self.locks[hall_id]:
                    # print("is conflict? ",self._is_time_conflict(existing_start, existing_end, start_time, end_time))
                    if self._is_time_conflict(existing_start, existing_end, start_time, end_time):
                        conflict = True
                        time.sleep(retry_interval)
                        waited_time += retry_interval
                        continue

                if not conflict:
                    # No conflicts, acquire lock
                    self.locks[hall_id][(start_time, end_time)] = Lock()
                    res = self.locks[hall_id][(start_time, end_time)].acquire()
                    self.logger.info(f'Lock Aquired, Hall id: {hall_id}, start: {start_time}, end: {end_time}')

                    # print("LM: lock acquired ")
                    return True
                

    def release_lock(self, hall_id, start_time, end_time):
        # with self._lock:
            start_time = datetime.fromisoformat(start_time)
            end_time = datetime.fromisoformat(end_time)

            if hall_id in self.locks and (start_time, end_time) in self.locks[hall_id]:
                self.locks[hall_id][(start_time, end_time)].release()
                self.logger.info(f'Lock Released, Hall id: {hall_id}, start: {start_time}, end: {end_time}')

                # print("LM: lock released")
                del self.locks[hall_id][(start_time, end_time)]
                # print("LM: lock deleted")

                # Notify waiting threads that the lock is released
                with self.conditions[hall_id][(start_time, end_time)]:
                    self.conditions[hall_id][(start_time, end_time)].notify_all()




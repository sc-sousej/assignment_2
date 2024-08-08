from threading import Lock, Condition
from collections import defaultdict
from datetime import datetime

class LockManager:
    def __init__(self):
        self.locks = defaultdict(dict)
        self.lock_conditions = defaultdict(dict)
        self.global_lock = Lock()

    def _is_time_conflict(self, existing_start, existing_end, new_start, new_end):
        return not (new_end <= existing_start or new_start >= existing_end)

    def acquire_lock(self, hall_id, start_time, end_time):
        start_time = datetime.fromisoformat(start_time)
        end_time = datetime.fromisoformat(end_time)

        with self.global_lock:
            if hall_id not in self.lock_conditions:
                self.lock_conditions[hall_id] = {}

            # Ensure condition variable for the time slot
            if (start_time, end_time) not in self.lock_conditions[hall_id]:
                self.lock_conditions[hall_id][(start_time, end_time)] = Condition()

        condition = self.lock_conditions[hall_id][(start_time, end_time)]
        with condition:
            while True:
                conflict = False
                with self.global_lock:
                    # Check for any time conflicts
                    for (existing_start, existing_end) in self.locks[hall_id]:
                        if self._is_time_conflict(existing_start, existing_end, start_time, end_time):
                            conflict = True
                            break

                    if not conflict:
                        # No conflicts, acquire lock
                        self.locks[hall_id][(start_time, end_time)] = Lock()
                        self.locks[hall_id][(start_time, end_time)].acquire()
                        return True

                # Wait for the lock to become available
                condition.wait()

    def release_lock(self, hall_id, start_time, end_time):
        start_time = datetime.fromisoformat(start_time)
        end_time = datetime.fromisoformat(end_time)

        with self.global_lock:
            if hall_id in self.locks and (start_time, end_time) in self.locks[hall_id]:
                self.locks[hall_id][(start_time, end_time)].release()
                del self.locks[hall_id][(start_time, end_time)]

                # Notify waiting threads that the lock is released
                self.lock_conditions[hall_id][(start_time, end_time)].notify_all()

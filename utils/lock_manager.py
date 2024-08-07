from threading import Lock, Condition
from collections import defaultdict, deque
from datetime import datetime

class LockManager:
    def __init__(self):
        self.locks = defaultdict(dict)
        self.conditions = defaultdict(dict)

    def _is_time_conflict(self, existing_start, existing_end, new_start, new_end):
        return not (new_end <= existing_start or new_start >= existing_end)

    def acquire_lock(self, hall_id, start_time, end_time):
        start_time = datetime.fromisoformat(start_time)
        end_time = datetime.fromisoformat(end_time)

        if hall_id not in self.locks:
            self.locks[hall_id] = {}
            self.conditions[hall_id] = {}

        # Ensure condition variable for the time slot
        if (start_time, end_time) not in self.conditions[hall_id]:
            self.conditions[hall_id][(start_time, end_time)] = Condition()

        with self.conditions[hall_id][(start_time, end_time)]:
            while True:
                # Check for any time conflicts
                conflict = False
                for (existing_start, existing_end) in self.locks[hall_id]:
                    if self._is_time_conflict(existing_start, existing_end, start_time, end_time):
                        conflict = True
                        break

                if not conflict:
                    # No conflicts, acquire lock
                    self.locks[hall_id][(start_time, end_time)] = Lock()
                    self.locks[hall_id][(start_time, end_time)].acquire()
                    print("LM: lock acquired")
                    return True
                else:
                    print("waiting for lock to become available")
                    # Wait for the lock to become available
                    self.conditions[hall_id][(start_time, end_time)].wait()

    def release_lock(self, hall_id, start_time, end_time):
        start_time = datetime.fromisoformat(start_time)
        end_time = datetime.fromisoformat(end_time)

        if hall_id in self.locks and (start_time, end_time) in self.locks[hall_id]:
            self.locks[hall_id][(start_time, end_time)].release()
            print("LM: lock released")
            del self.locks[hall_id][(start_time, end_time)]
            print("LM: lock deleted")

            # Notify waiting threads that the lock is released
            with self.conditions[hall_id][(start_time, end_time)]:
                self.conditions[hall_id][(start_time, end_time)].notify_all()





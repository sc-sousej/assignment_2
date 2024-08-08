from utils.lock_manager import LockManager
ob1= LockManager()
ob2 = LockManager()
if ob1 is ob2:
    print("panic")
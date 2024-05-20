import time
import os
from func_timeout import func_timeout, FunctionTimedOut

def my_test(name):
    print("now running, name={}, pid={}".format(name, os.getpid()))
    time1 = time.time()
    time.sleep(2)
    time2 = time.time()
    span = (time2 - time1)
    print("process has ended after {}s.".format(span))
    return 100
    
if __name__ == "__main__":
    try:
        output = func_timeout(3, my_test, args=("test", ))
        print(output)
    except FunctionTimedOut as e:
        print(e)
        # print('process timed out.')
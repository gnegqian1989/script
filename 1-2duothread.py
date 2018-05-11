#!/usr/bin/python
#coading:utf-8

import threading ,time
def fun(var):
    time.sleep(1)
    print(var)
for i in range(10):
    t=threading.Thread(target = fun ,args =(i,))
    t.start()
print('end')
#!/usr/bin/python
#coading:utf-8

import os
import time
print ("cpu dedecting")
flag = True
while flag:
    os.system(r"top - n 1 >file1.txt")
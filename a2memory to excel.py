#!/usr/bin/python
# coding=utf-8


# 记录内存数据total到excel文件中
import time
import subprocess
import xlwt

package_name_mysdk = 'com.esint.publicsecurity'


def getPSS(package_name):
    # 用adb获取信息adb shell "dumpsys meminfo com.tcl.live | grep "TOTAL""
    p = subprocess.Popen('adb shell "dumpsys meminfo ' + package_name + ' | grep "TOTAL""', stdout=subprocess.PIPE,
                         stderr=subprocess.PIPE)
    text = p.stdout.read()
    listoftext = text.split()
    print ('PSS=',listoftext[1])
    return int(listoftext[1])


time_start = 0
time_end = 0

# 创建新的工作薄
book = xlwt.Workbook(encoding='utf-8', style_compression=0)
# 创建新的sheet,并命名为PSS
sheet_sdk = book.add_sheet('PSS-SDK', cell_overwrite_ok=True)
sheet_sdk.write(0, 0, "time")
sheet_sdk.write(0, 1, "PSS")

# excel表格的行（row）、列（col）
row = 1
col = 0

# 测试时间为3600s=1h
while time_end <= 60:
    # 获取当前时间
    timeNow = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
    print(timeNow)
    sheet_sdk.write(row, col, timeNow)
    try:
        pss_sdk = getPSS(package_name_mysdk)
        sheet_sdk.write(row, col + 1, pss_sdk)
    except:
        print(time.strftime('%Y-%m-%d  %H:%M:%S', time.localtime(time.time())) , "process has been shuoutdown!")

    row += 1
    time_end += 1
    # 获取pss total值时间间隔10s
    time.sleep(10)
    book.save(r"D:\\test\\pss.xls")
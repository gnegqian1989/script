#! /usr/bin/python3
# -*- coding: utf-8 -*-

import os, sys, time, logging,subprocess,xlwt

# 下列时间单位均为秒
# 执行时间
# exec_time = 15 * 60 * 60  # 10 hours, 可改成60s供测试该脚本
exec_time = 60
# 记录内存间隔时间，exec_time/exec_interval + 1 即为记录内存次数
exec_interval = 10  # 10 s
# 导出hprof文件间隔
# dump_interval = 60 * 60  # 1 hour, 可改成30s供测试该脚本
dump_interval =  20

time_passed = 0
# 打印提示间隔次数，以查看当前进度
print_interval = 1
packageName = "com.esint.publicsecurity"
bulid_type = ""

# 所有产生文件的输出目录，必须指定且存在
OUTPUT_DIR = os.path.join(os.path.expanduser('D:\\test'))  # 目录"~/test"

logger = logging.getLogger('memoryleak')
FILE_LOG = True
LOG_LEVEL = logging.DEBUG


def init_logger():
    logger.setLevel(LOG_LEVEL)
    # create formatter
    # [%(filename)s:%(lineno)d] 代码位置，暂不配
    log_format = logging.Formatter("%(asctime)s %(name)s %(levelname)-8s: %(message)s")

    def add_ch():
        # create console handler and set level to debug
        ch = logging.StreamHandler()
        ch.setLevel(LOG_LEVEL)
        ch.setFormatter(log_format)
        # add handler to logger
        logger.addHandler(ch)

    def add_fh():
        logfile = os.path.join(OUTPUT_DIR, "memoryleak_" + time.strftime('%Y%m%d%H%M%S') + ".log")
        fh = logging.FileHandler(logfile)
        fh.setLevel(LOG_LEVEL)
        fh.setFormatter(log_format)
        logger.warning('log will be outputed to console and file:[%s]' % logfile)
        logger.addHandler(fh)

    add_ch()
    if not (OUTPUT_DIR and os.path.isdir(OUTPUT_DIR) and os.access(OUTPUT_DIR, os.W_OK)):
        logger.error('OUTPUT_DIR: "%s" not exist or not writable, please check it up, exiting...')
        sys.exit(-1)
    if FILE_LOG:
        add_fh()


def start_monkey():
    # adb shell monkey -p com.gionee.filemanager --throttle 800 -v -v 300
    command = "adb shell monkey -p " + packageName
    command += " --ignore-crashes"
    command += " --ignore-timeouts"
    command += " --ignore-security-exceptions"
    command += " --ignore-native-crashes"
    command += " --monitor-native-crashes"
    command += " --throttle 800"
    command += " -v -v 1000000"
    command += " > " + os.path.join(OUTPUT_DIR, "monkeytest.log")
    logger.info("插入monkey命令：" + command)
    os.popen(command)


def record_memory():
    global time_passed
    if "eng" in bulid_type:
        memfile = os.path.join(OUTPUT_DIR, 'procrank.txt')
        # 第一次执行命令
        command = command1 = 'adb shell procrank | grep "' + packageName + '\|cmdline" > ' + memfile
        # 后续执行命令
        commandOther = 'adb shell procrank | grep ' + packageName + ' >> ' + memfile
    else:
        memfile = os.path.join(OUTPUT_DIR, 'meminfo.txt')
        command = command1 = 'adb shell dumpsys meminfo ' + packageName + \
                             ' | grep "Dalvik Heap" -A 14 -B 4 | grep -i "Private\|Total\|--" > ' + memfile
        commandOther = 'adb shell dumpsys meminfo ' + packageName + ' | grep TOTAL -m 1 >> ' + memfile

    exec_count = exec_time // exec_interval + 1
    logger.info("开始记录内存信息，待记录次数：" + str(exec_count))
    for i in range(exec_count):
        os.popen(command)  # 运行命令
        # 执行初始命令后切换为后续命令
        if i == 0:
            command = commandOther

        if i % print_interval == 0:
            logger.info("当前记录内存次数: " + str(i))

        if (time_passed) % dump_interval == 0:
            logger.info("当前dump hprof次数: " + str(time_passed // dump_interval))
            dumpheap(str(time_passed // dump_interval))

        time_passed += exec_interval
        time.sleep(exec_interval)  # 休息n秒，再进入下一个循环，也就是每隔n秒打印一次procrank的信息

    logger.info("记录内存信息结束")  # 运行完毕的标志


def dumpheap(name):
    command = "adb shell am dumpheap " + packageName + " /data/local/tmp/hprofs/"
    command += "count" + name + ".hprof"
    os.popen(command)




    def getPSS(package_name):
        # 用adb获取信息adb shell "dumpsys meminfo com.tcl.live | grep "TOTAL""
        p = subprocess.Popen('adb shell "dumpsys meminfo ' + package_name + ' | grep "TOTAL""', stdout=subprocess.PIPE,
                             stderr=subprocess.PIPE)
        text = p.stdout.read()
        listoftext = text.split()
        print('PSS=', listoftext[1])
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
            pss_sdk = getPSS(packageName)
            sheet_sdk.write(row, col + 1, pss_sdk)
        except:
            print(time.strftime('%Y-%m-%d  %H:%M:%S', time.localtime(time.time())), "process has been shuoutdown!")

        row += 1
        time_end += 1
        # 获取pss total值时间间隔10s
        time.sleep(10)
        book.save(r"d:\\pss.xls")




def stop_monkey():
    # adb shell kill -9 `adb shell ps | grep com.android.commands.monkey | awk '{print $2}'`
    pid = os.popen("adb shell ps | grep monkey | awk '{print $2}'").read()
    pid = pid.replace("\n", "")
    logger.info("monkey pid is: " + pid + ", kill it")
    os.system("adb shell kill " + pid)


def copyheap():
    logger.info("开始导出hprof文件...")
    os.system("adb pull /data/local/tmp/hprofs/ " + OUTPUT_DIR)
    os.system("adb shell rm -r /data/local/tmp/hprofs")
    logger.info("导出hprof文件结束")



    # 清空及建立hprof文件存放目录
    if 'hprofs' in os.popen('adb shell ls /data/local/tmp').read():
        logger.info('在设备中清除上次运行产生的临时目录"/data/local/tmp/hprofs"...')
        os.system("adb shell rm -r /data/local/tmp/hprofs")
    logger.info('在设备中新建临时目录"/data/local/tmp/hprofs"...')
    os.system("adb shell mkdir -p /data/local/tmp/hprofs")


def main():
    init_logger()
    start_monkey()


    # 循环进行，程序主体
    record_memory()
    getPSS()
    stop_monkey()
    copyheap()


if __name__ == '__main__':
    main()
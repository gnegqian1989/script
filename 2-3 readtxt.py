#!/usr/bin/python
#coading:utf-8

# 提取txt中指定字段

def iterdatainfile(filename,spliter = '\t'):
    with open(filename,'rt') as handle:
        for In in handle:
            yield In.split(spliter)
focue, LF = 1,'\n'
with open("output.txt",'wt') as handle:
    handle.writelines([row[focue] + LF
                       for row in iterdatainfile('test.txt',spliter = 'test.txt',spliter='|')])

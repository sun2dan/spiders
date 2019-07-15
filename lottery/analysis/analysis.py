import sys, os
import sqlite3
import random

''' 数据分析及生成
1.假设将要抽10560次（16和33的公倍数）理想状态下，蓝球出现次数应该为 10560/16=660 次，红球出现的次数应该为 10560*6/33=1920 次；
2.现在已经抽了2420次，蓝球实际出现 b1、b2……、b16 次，红球实际出现 r1、r2……、r33 次；
用1中的理想状态下的次数，分别减去各个数字已经出现的次数，相加分别得到红球、蓝球集合；
3.产生随机数，生成数字；红球每生成一个数字，需要改变刚才算好的集合，因为该红球在本次抽奖中不会再出现；
'''
# 原始数据
red_map = {}
blue_map = {}
# 排除数字集合
red_exclude = {}
blue_exclude = {}
# 实时集合
red_set = []
blue_set = []

# 红球、蓝球每个号码理想状态下出现的次数
blue_count = 660
red_count = 1920

def main():
    get_data()
    fill_set()
    random.shuffle(red_set)
    random.shuffle(blue_set)
    print(red_set, blue_set)

# 生成目标集合，红球选6个，蓝球选1个
def create_target():

    pass

# 生成数字集合
def fill_set():
    fill_num(blue_map, blue_exclude, blue_set, blue_count)
    fill_num(red_map, red_exclude, red_set, red_count)

# 生成数字集合公共方法
def fill_num(col_map, col_ex, col_set, col_count):
    for num in col_map:
        count = col_map[num]
        if col_ex.get(num, 0) > 0:
            continue
        for n in range(0, col_count - count):
            col_set.append(num)

# 获取库里边的数据
def get_data():
    db_name = '../lottery.db'
    conn = sqlite3.connect(db_name)
    cur = conn.cursor()
    sql = 'select num,count(num) from raw where type=0 group by num'
    cur.execute(sql)
    red_res = cur.fetchall()

    sql = 'select num,count(num) from raw where type=1 group by num'
    cur.execute(sql)
    blue_res = cur.fetchall()
    conn.close()

    for row in red_res:
        red_map[row[0]] = row[1]
    for row in blue_res:
        blue_map[row[0]] = row[1]

if __name__ == "__main__":
    main()

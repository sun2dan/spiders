import sys, os, time
import sqlite3
import random

''' 数据分析及生成
1. 取出库中实际的开奖次数，用概率乘开奖次数得出理想状态下出现的次数；
2. 现在已经抽了2420次，假设已经完成了50%，即总次数为2420*2=4840次，2-实际次数/应该出现的次数 = 下次出现的"实际"概率，
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
blue_count = 0
red_count = 0
# 假设抽取的总次数（和概率相乘，实际是想要保留概率的几位小数）
sum_count = 10000

def main():
    get_data()

    global red_exclude
    global blue_exclude
    red_exclude = {}
    blue_exclude = {}

    global blue_set
    blue_set = []
    fill_num(blue_map, blue_exclude, blue_set, blue_count)
    random.shuffle(blue_set)
    blue_rand = get_random(len(blue_set))
    blue_target = blue_set[blue_rand]

    res_red = []
    global red_set
    for n in range(0, 6):
        red_set = []
        fill_num(red_map, red_exclude, red_set, red_count)
        if len(red_set) == 0:
            print('len为0')
            continue
        random.shuffle(red_set)
        red_rand = get_random(len(red_set))
        red_target = red_set[red_rand]
        res_red.append(red_target)
        red_exclude[red_target] = 1

    res_red.sort()

    res = []
    for n in res_red:
        res.append(str(n).rjust(2, '0'))
    blue_num = str(blue_target).rjust(2, '0')
    print(', '.join(res), '+', blue_num)

def get_random(count):
    time.sleep(random.random() ** random.random())
    random.seed(random.random() ** random.random())
    return random.randint(0, count - 1)

# 生成数字集合公共方法
def fill_num(col_map, col_ex, col_set, col_count):
    for num in col_map:
        count = col_map[num]
        if col_ex.get(num, 0) > 0:
            continue
        # print((1 - count / col_count))
        end = int((1 - count / col_count) * sum_count)
        for n in range(0, end):
            col_set.append(num)
    # range_end = sum_count * times / 2 - len(red_set)

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

    sql = 'select count(num) from raw where type=1'
    cur.execute(sql)
    total_res = cur.fetchone()
    conn.close()

    for row in red_res:
        red_map[row[0]] = row[1]
    for row in blue_res:
        blue_map[row[0]] = row[1]

    total = 0
    if total_res:
        total = total_res[0]
    else:
        print('未查到总次数')

    global blue_count, red_count
    # 当前次数2倍的集合里，理想状态应该出现的次数；可能会有除不尽的情况
    blue_count = total / 16 * 2  # total/16，一倍集合里应该出现的次数
    red_count = total * 6 / 33 * 2

if __name__ == "__main__":
    for n in range(0, 10):
        main()

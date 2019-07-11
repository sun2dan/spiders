import sys, os
import sqlite3

class DBA():
    db_name = 'lottery.db'
    table_name = 'raw'

    def __init__(self):
        conn = sqlite3.connect(self.db_name)
        print("Open database successfully")
        table_name = self.table_name

        sql = '''
            CREATE TABLE "%s" (
                "id"	    INTEGER PRIMARY KEY AUTOINCREMENT,
                "period"	    TEXT, -- 期号   
                "r1"	INT,   -- 红球1
                "r2"	INT,   -- 红球2
                "r3"	INT,   -- 红球3
                "r4"	INT,   -- 红球4
                "r5"	INT,   -- 红球5
                "r6"	INT,   -- 红球6
                "b"	    INT,   -- 蓝球
                "amount"    INT,   -- 销售额
                "first"     INT,   -- 一等奖中奖数目
                "second"    INT,   -- 二等奖中奖数目
                "openTime"  DateTime -- 开奖时间
            )''' % table_name
        try:
            conn.execute(sql)
        except:
            print('table %s already exists' % table_name)
            conn.execute('DROP TABLE ' + table_name)
            conn.execute(sql)

        conn.commit()
        print('table %s created' % table_name)

    def get_empty_obj(self):
        data = {}
        data["id"] = ''
        data["period"] = ''
        data["r1"] = ''
        data["r2"] = ''
        data["r3"] = ''
        data["r4"] = ''
        data["r5"] = ''
        data["r6"] = ''
        data["b"] = ''
        data["amount"] = ''
        data["first"] = ''
        data["second"] = ''
        data["openTime"] = ''
        return data

    def insert(self, data):
        conn = sqlite3.connect(self.db_name)
        sql = 'insert into ' + self.table_name + ''' (period, r1,r2,r3,r4,r5,r6,b,amount,first,second,openTime) values ('{period}', {r1},{r2},{r3},{r4},{r5},{r6},{b},{amount},{first},'{second}', '{openTime}' )'''.format(
            **data)
        # print(sql)
        conn.execute(sql)
        conn.commit()
        conn.close()

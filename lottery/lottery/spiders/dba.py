import sys, os
import sqlite3

class DBA():
    db_name = 'lottery.db'
    table_name = 'raw'

    def __init__(self):
        # 如果数据库已经存在，不重新初始化
        if os.path.exists('lottery.db'): return

        conn = sqlite3.connect(self.db_name)
        print("Open database successfully")
        table_name = self.table_name

        sql = '''
            CREATE TABLE "%s" (
                "id"	    INTEGER PRIMARY KEY AUTOINCREMENT,
                "period"    INT,  -- 期号
                "num"       INT,  -- 号码
                "type"      INT   -- 类型：红球-0 蓝球-1
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
        data["num"] = ''
        data["type"] = ''
        return data

    def insert(self, data):
        conn = sqlite3.connect(self.db_name)
        sql = 'insert into ' + self.table_name + ''' (period, num, type) values 
            ({period}, {num}, {type})'''.format(**data)
        print(sql)
        conn.execute(sql)
        conn.commit()
        conn.close()

    def clear(self):
        conn = sqlite3.connect(self.db_name)
        sql = 'delete from raw where 1=1'
        conn.execute(sql)
        conn.commit()
        conn.close()

    # 获取新的期数
    def get_max_period(self):
        db_name = self.db_name
        conn = sqlite3.connect(db_name)
        cur = conn.cursor()
        sql = 'select max(period) from raw'
        cur.execute(sql)
        res = cur.fetchone()
        conn.close()
        if res is not None and res[0]:
            return res[0]
        return 0

import sys, os
import sqlite3

class DBA2():
    db_name = 'job.db'
    table_name = 'raw2'

    def __init__(self):
        conn = sqlite3.connect(self.db_name)
        print("Open database successfully")
        table_name = self.table_name

        sql = '''
            CREATE TABLE "%s" (
                "id"	    INTEGER PRIMARY KEY AUTOINCREMENT,
                "title"	    TEXT,   
                "content"	TEXT,   -- 仕事の内容
                "claim"	    TEXT,   -- 求めている人材
                "addr"	    TEXT,   -- 勤務地
                "salary"	TEXT,   -- 給与
                "worktime"	TEXT,   -- 勤務時間
                "holiday"	TEXT,   -- 休日・休暇
                "welfare"	TEXT,   -- 待遇・福利厚生
                "during"	TEXT,
                "tags"	    TEXT,
                "company"	TEXT,
                "desc"      TEXT, 
                "url"       TEXT,   -- 数据来源url
                "ntype"     TEXT,   -- ntype 类型
                "createdTime" DateTime DEFAULT (datetime('now', 'localtime'))
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
        data["title"] = ''
        data["content"] = ''
        data["claim"] = ''
        data["addr"] = ''
        data["salary"] = ''
        data["worktime"] = ''
        data["holiday"] = ''
        data["welfare"] = ''
        data["during"] = ''
        data["tags"] = ''
        data["company"] = ''
        data["desc"] = ''
        data["url"] = ''
        data["ntype"] = ''
        data["createdTime"] = ''
        return data

    def insert(self, data):
        conn = sqlite3.connect(self.db_name)
        sql = '''insert into %s (title, content, claim, addr, salary, worktime, holiday, welfare, during, tags, company, desc, url, ntype) values ('{title}', '{content}', '{claim}', '{addr}', '{salary}', '{worktime}', '{holiday}', '{welfare}', '{during}', '{tags}', '{company}', '{desc}', '{url}', '{ntype}' )''' % self.table_name.format(
            **data)
        # print(sql)
        conn.execute(sql)
        conn.commit()
        conn.close()

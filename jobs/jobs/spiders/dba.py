import sys, os
import sqlite3

class DBA():
    db_name = 'job.db'

    def __init__(self):
        conn = sqlite3.connect(self.db_name)
        print("Open database successfully")

        sql = '''
            CREATE TABLE "raw" (
                "id"	INTEGER PRIMARY KEY AUTOINCREMENT,
                "title"	TEXT,
                "content"	TEXT,
                "claim"	TEXT,
                "addr"	TEXT,
                "salary"	TEXT,
                "worktime"	TEXT,
                "holiday"	TEXT,
                "welfare"	TEXT,
                "during"	TEXT,
                "tags"	TEXT,
                "company"	TEXT,
                "desc" TEXT, 
                "createdTime" DateTime DEFAULT 'datetime()'
            )'''
        try:
            conn.execute(sql)
        except:
            print('table raw already exists')
            conn.execute('DROP TABLE raw')
            conn.execute(sql)

        conn.commit()
        print('table raw created')

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
        data["createdTime"] = ''
        return data

    def insert(self, data):
        conn = sqlite3.connect(self.db_name)
        sql = '''insert into raw (title, content, claim, addr, salary, worktime, holiday, welfare, during, tags, company, desc) values ('{title}', '{content}', '{claim}', '{addr}', '{salary}', '{worktime}', '{holiday}', '{welfare}', '{during}', '{tags}', '{company}', '{desc}' )'''.format(
            **data)
        conn.execute(sql)
        conn.commit()
        conn.close()

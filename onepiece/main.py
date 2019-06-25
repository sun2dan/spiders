import re, requests, os, time
import urllib.request
import sqlite3
import ssl

prefix = 'https://one-piece.com'
db_name = 'character.db'
records = {
    'no_img': [],  # 没有图片
    'no_desc': [],  # 没有描述
    'special': []  # 有特殊描述
}

# https://one-piece.com/assets/images/anime/character/data/Kuromarimo/img.jpg
# https://one-piece.com/assets/images/anime/character/data/Kuromarimo/face.jpg
# https://one-piece.com/log/character/detail/kuzan.html

def main():
    ssl._create_default_https_context = ssl._create_unverified_context
    tar_url = 'https://one-piece.com/log/character.html?p='
    fruit_url = 'https://one-piece.com/log/character/devilfruit.html?p='
    limits = [26, 4]  # 角色有26页，恶魔果实有4页
    print(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))
    # 初始化
    init_db()

    # 收集基本信息+恶魔果实数据
    idx = 1
    while idx <= limits[0]:
        get_base(tar_url + str(idx))
        idx += 1
    index = 1
    while index <= limits[1]:
        get_fruit(fruit_url + str(index))
        index += 1

    where = ''
    list = get_list(where)

    # 根据收集到的第一波数据获取第二波数据-详情信息 # detail_url = 'https://one-piece.com/log/character/detail/Amazon.html'
    for arr in list:
        get_details(arr[2])

    # 下载图片
    list = get_list('')
    # # 查找下载错误的图片
    # names = []
    # for root, dirs, files in os.walk('./images/img/'):
    #     for file_item in files:
    #         img_path = root + '/' + str(file_item)
    #         size = os.path.getsize(img_path)
    #         name = re.sub(r'\.\w+$', '', file_item)
    #         names.append('\'' + name + '\'')
    #         if size == 269422:
    #             name = re.sub(r'\.\w+$', '', file_item)
    #             names.append('\'' + name + '\'')
    #             # os.remove(img_path)
    #
    # print(len(names), names)
    # where = ' where ename in ({0})'.format(','.join(names))
    # list = get_list(where)

    # 下载图片
    for data in list:
        ename = data[2]
        # time.sleep(1) # download_img(data[5], 'face', ename)
        download_with_headers(data[5], 'face', ename)
        download_with_headers(data[6], 'img', ename)

    print(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))

# 根据where条件获取list
def get_list(where):
    conn = sqlite3.connect(db_name)
    sql = 'select * from role ' + where
    cursor = conn.execute(sql)
    list = []
    for row in cursor:
        list.append(row)
    conn.close()
    return list

# 获取desc、birthday、attr、img
def get_details(ename):
    url = 'https://one-piece.com/log/character/detail/' + ename + '.html'
    page = urllib.request.urlopen(url)
    html = page.read().decode('utf-8')
    page.close()

    print(url, "开始处理 url")
    data = get_data()
    data['ename'] = ename

    # img
    groups = re.search(r'<p class="contImg charaMainv"><img src="([\w\d\/\.]+)"', html)
    if groups is None:
        records['no_img'].append(url)
        print('没有找到图片')
    else:
        data['img'] = prefix + groups.group(1)

    # 属性
    pattern = re.compile(r'<dt>([^<>]+)</dt>\s+<dd>\s{0,}([^<>]+)</dd>')
    list = pattern.findall(html)
    result = []
    for arr in list:
        a = re.sub(r'(^\s+)|(\s+$)', '', arr[0])
        b = re.sub(r'(^\s+)|(\s+$)', '', arr[1])
        result.append({'key': a, 'value': b})

    attrs = []
    # 特殊属性
    for item in result:
        key = item['key']
        val = item['value']
        if key == '誕生日':
            data['birthday'] = val
        elif key == '懸賞金':
            data['bounty'] = val
        elif key == '通称':
            data['nickname'] = val
        else:
            attrs.append(key + ' : ' + val)
    # 普通属性
    data['attr'] = ' | '.join(attrs)

    # desc  普通描述
    groups = re.search(r'<p>([^<>]+)</p>\s{0,}(<br\s?/>){0,}\s{0,}</section>', html)
    if groups is None:
        print('没有普通描述')
        data['desc'] = get_special_desc(html, url)
    else:
        data['desc'] = groups.group(1)
    print(data)
    update_role(data)

# 获取特殊描述
def get_special_desc(html, url):
    desc = ''
    group = re.search(r'<section([\s\S]+)</section>', html)
    if group is None:
        print('没有普通描述和特殊描述')
    else:

        res = group.group(1)
        pattern = re.compile(r'(<(p)>([^<>]+)</p>)|(<(h2) class="t f17">([^<>]+)</h2>)')
        list = pattern.findall(res)
        if len(list) == 0:
            records['no_desc'].append(url)
            print('没有普通描述和特殊描述')
        else:
            records['special'].append(url)
            for arr in list:
                if arr[1] == 'p':
                    desc += arr[2] + '\n'
                elif arr[4] == 'h2':
                    desc += '\n' + arr[5] + '\n'
    return desc

def update_role(data):
    sql = r'''update role set 
                        nickname='{nickname}', img='{img}', birthday='{birthday}', bounty='{bounty}' , attr='{attr}', desc='{desc}' 
                        where ename='{ename}' '''.format(**data)
    conn = sqlite3.connect(db_name)
    conn.execute(sql)
    conn.commit()
    conn.close()

# 获取基本信息：日文名称、英文名称、头像
def get_base(url):
    page = urllib.request.urlopen(url)
    # html = str(page.read().decode('utf-8'))
    html = page.read().decode('utf-8')
    page.close()

    pattern = re.compile(
        r'<a\s+class="boxRadius"\s+href="/log/character/detail/([\w\d\-_]+).html">\s?<span class="detailBox">\s?<p class="charaName">([^<>]+)</p>\s?</span>\s?<p class="thumb">\s?<img\s+src="([\w\d\/\.]+)" alt="[\w\d]+"\s?/>\s?</p>\s?</a>')
    list = pattern.findall(html)
    print(url, len(list))
    if len(list) > 0:
        for obj in list:
            insert_base(obj)

def insert_base(arr):
    face = prefix + arr[2]
    data = get_data()
    data["jname"] = arr[1]
    data["face"] = face
    data["ename"] = arr[0]
    print(data['ename'])

    conn = sqlite3.connect(db_name)
    sql = '''insert into role (jname, rname, ename, nickname, face, img, birthday, bounty, attr, desc)
      values ('{jname}', '{rname}', '{ename}', '{nickname}', '{face}', '{img}', '{birthday}', '{bounty}', '{attr}', '{desc}')'''.format(
        **data)
    conn.execute(sql)
    conn.commit()
    conn.close()

# 获取果实
def get_fruit(url):
    page = urllib.request.urlopen(url)
    html = page.read().decode('utf-8')
    page.close()

    pattern = re.compile(
        r'<a class="boxRadius" href="[\w\d\/]+/([\w\d_\-]+)\.html"><span class="detailBox"><p\s+class="charaName">[^<>]+</p><p\s+class="f13 t subComment">([^<>]+)\s+([^<>]+)(<br\s+/>([^<>]+)\s+([^<>]+))?<br\s+/>(([^<>]+))?</p>')
    list = pattern.findall(html)
    print(url, len(list))
    if len(list) > 0:
        for obj in list:
            insert_fruit(obj)

def insert_fruit(arr):
    data = {}
    data["ename"] = arr[0]
    data["name"] = arr[2] + format_mul_val(arr[5])
    data["type"] = arr[1] + format_mul_val(arr[4])
    data["model"] = arr[len(arr) - 1]

    conn = sqlite3.connect(db_name)
    sql = '''insert into devilfruit (ename, name, type, model) values ('{ename}', '{name}', '{type}', '{model}')'''.format(
        **data)
    conn.execute(sql)
    conn.commit()
    conn.close()

def format_mul_val(val):
    n = val
    if val != '':
        n = ' | ' + val
    return n

def init_db():
    conn = sqlite3.connect(db_name)
    print("Opened database successfully")

    sql = '''create  table role(
                [id] integer PRIMARY KEY  AUTOINCREMENT UNIQUE NOT NULL
                ,[jname] text
                ,[ename] text
                ,[rname] text
                ,[nickname] text
                ,[face] text
                ,[img] text
                ,[birthday] text
                ,[bounty] text
                ,[attr] text
                ,[desc] text 
              );
    '''
    try:
        conn.execute(sql)
    except:
        print('table role already exists')
        conn.execute('DROP TABLE role')
        conn.execute(sql)

    # table devil
    sql1 = '''create  table devilfruit(
               [id] integer PRIMARY KEY UNIQUE NOT NULL
                ,[ename] text UNIQUE NOT NULL
                ,[name] text
                ,[type] text
                ,[model] text
              );
    '''
    try:
        conn.execute(sql1)
    except:
        print('table devilfruit already exists')
        conn.execute('DROP TABLE devilfruit')
        conn.execute(sql1)

    conn.commit()
    print('table role and devilfruit created')

def get_data():
    data = {}
    data["jname"] = ''
    data["rname"] = ''
    data["ename"] = ''
    data["nickname"] = ''
    data["face"] = ''
    data["img"] = ''
    data["birthday"] = ''
    data["bounty"] = ''
    data["attr"] = ''
    data["desc"] = ''
    return data

# -------------------- 下载图片相关 --------------------
'''
图片有两种，一种可以直接下载：https://one-piece.com/assets/images/anime/character/data/izo/img.jpg
一种需要配置请求头才可以下载：https://one-piece.com/assets/uploads/anime/character/characters/20180820
/46c2d42ca1a4d8f509a8d0e5fd86d7b6.jpg
'''
# 获取本地文件地址
def get_local_path(img_url, ename, dir):
    group = re.search(r'\/[\w\d]+(\.\w+)$', img_url)
    stuff = ''
    if group is not None and (len(group.groups()) > 0):
        stuff = group.group(1)
    return r'./images/{0}/{1}'.format(dir, ename + stuff)

# 下载图片，设置request headers，设置了多个header项，因为懒得去找该网站到底是根据哪一项来做限制的
def download_with_headers(img_url, dir, ename):
    if img_url == '':
        return print(ename, dir, '地址为空')

    headers = {
        'Accept': 'image/webp,image/apng,image/*,*/*;q=0.8',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'zh-CN,zh;q=0.9,ja;q=0.8',
        'Cache-Control': 'no-cache',
        'Connection': 'keep-alive',
        'Cookie': '_ga=GA1.2.1713471329.1531883956; _gid=GA1.2.1810287860.1532905602; _gat=1',
        'Host': 'one-piece.com',
        'Pragma': 'no-cache',
        'Referer': 'https://one-piece.com/log/character.html?p=1',
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.75 Safari/537.36'
    }
    local_path = get_local_path(img_url, ename, dir)
    print('download', ename, dir, img_url, local_path)

    r = requests.get(img_url, headers=headers)
    image = r.content

    with open(local_path, 'wb') as fb:
        fb.write(image)

# 下载图片(不设置request headers)
def download_img(img_url, dir, ename):
    if img_url == '':
        return print(ename, dir, '地址为空')
    local_path = get_local_path(img_url, ename, dir)

    print('download', ename, dir, img_url, local_path)
    urllib.request.urlretrieve(img_url, local_path)

if __name__ == "__main__":
    main()
    pass

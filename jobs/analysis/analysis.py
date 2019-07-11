import sys, os, re
from os import path
import sqlite3

os.environ['FONT_PATH'] = '/System/Library/Fonts/ヒラギノ明朝 ProN.ttc'
from wordcloud import WordCloud

DEBUG = True  # 调试，会生成词云的原始文件，便于和结果对比，查找原始词汇
db_name = '../job.db'
# 公共where条件（有招聘时间）
where = ' where 1=1 and during<>"" '  # 默认为rikunabi中的新数据 + tenshoku中的数据

# where 1=1 # 所有数据
# where 1=1 and during<>""  # rikunabi中的新数据 + tenshoku中的数据
# where 1=1 and during<>"" and ntype<>"ten"  # rikunabi 中的新数据
# where 1=1 and ntype<>"ten"  # rikunabi 中的所有数据
# where 1=1 and ntype="ten"  # tenshoku 中的数据

def main():
    list = get_all()
    basic_analysis(list)
    wordcloud_skill(list)
    wordcloud_addr(list)

# 基本分析
def basic_analysis(list):
    all_len = len(list)  # 总记录数

    conn = sqlite3.connect(db_name)
    cur = conn.cursor()

    # 每家公司的信息发布情况
    sql = 'select company, count(company) from total {} group by company order by count(company) desc'.format(where)
    cur.execute(sql)
    res = cur.fetchall()
    company_len = len(res)
    count_map = {}

    for row in res:
        name = row[0]
        count = row[1]
        if count_map.get(count, '') == '':
            count_map[count] = [name]
        else:
            count_map[count].append(name)
    print('{} 家公司发布了 {} 条招聘信息，平均每家发布 {:.2f} 条信息'.format(company_len, all_len, all_len / company_len))
    len1 = len(count_map[1])
    print('有 {} 家公司只发布了一条信息，占总公司数的 {:.2f}%'.format(len1, len1 / company_len * 100))
    max_count = 1
    for key in count_map.keys():
        if key > max_count:
            max_count = key
    max_arr = count_map[max_count]
    print('发布招聘信息最多的公司有 {} 家，分别发布了 {} 条'.format(len(max_arr), max_count))

    # 多少家公司在东京/在东京有分公司
    sql = 'select count(distinct (company)) from total {0} and addr like "%東京%"'.format(where)
    cur.execute(sql)
    res = cur.fetchone()
    n = res[0]
    print('有 {} 家公司在东京/在东京有分公司，占总公司数的 {:.2f}%'.format(n, n / company_len * 100))

    # 多少公司不限学历
    sql = 'select count(id) from total {} and (claim like "%学歴不問%" or claim like "%学歴・%不問%")'.format(where)
    cur.execute(sql)
    res = cur.fetchone()
    n = res[0]
    print('{} 个招聘明确标注了不限学历，占总数的 {:.2f}%'.format(n, n / all_len * 100))

    conn.close()

# 技能词云
def wordcloud_skill(list):
    name = 'skill'
    img_path = 'src/%s.png' % name
    skill_arr = []

    for row in list:
        skill_arr.append(format_skill(row[2]))  # content 工作内容
        skill_arr.append(format_skill(row[3]))  # claim 任职要求
        skill_arr.append(format_skill(row[10]) + '\n')  # tags 标签
    skill_str = '\n'.join(skill_arr)
    create_wordcloud(skill_str, img_path)
    write_file(name, skill_str, list, [2, 3, 10])

# 工作地点词云
def wordcloud_addr(list):
    name = 'addr'
    img_path = './src/%s.png' % name
    addr_arr = []
    for row in list:
        addr_arr.append(format_addr(row[4]))  # addr 地址
    addr_str = '\n'.join(addr_arr)
    create_wordcloud(addr_str, img_path)
    write_file(name, addr_str, list, [4])

# 创建词云 + 保存图片
def create_wordcloud(text, img_path):
    # 官方demo代码修改
    d = path.dirname(__file__) if "__file__" in locals() else os.getcwd()
    # text = open(path.join(d, file_path)).read()
    wordcloud = WordCloud().generate(text)

    # Display the generated image:  # the matplotlib way:
    import matplotlib.pyplot as plt
    plt.imshow(wordcloud, interpolation='bilinear')
    plt.axis("off")

    # font_path = '/System/Library/Fonts/ヒラギノ明朝 ProN.ttc'
    wordcloud = WordCloud(max_font_size=60, width=400, height=300, collocations=False,
                          # font_path=font_path,
                          scale=2).generate(text)  # collocations=False，不统计搭配词
    plt.figure()
    plt.imshow(wordcloud, interpolation="bilinear")
    plt.axis("off")
    plt.show()

    wordcloud.to_file(img_path)

# 将原始文本和过滤之后的文本存储到文件中，方便查看对比
def write_file(name, text, list, idx_arr):
    if not DEBUG: return
    file_raw = 'src/%s.txt' % (name + '_raw')
    file_filter = 'src/%s.txt' % (name + '_filter')

    # 过滤之后的数据 src/add_filter.txt
    with open(file_filter, "w") as f:  # w-覆盖
        f.write(text)
        f.close()

    # 原始数据文件 src/add_raw.txt，如果存在就不重写，因为原始数据没有经过处理，不用每次重新生成
    if os.path.exists(file_raw): return
    with open(file_raw, "w") as f:
        for row in list:
            for idx in idx_arr:
                f.write(row[idx] + '\n')
            f.write('\n')
        f.close()

# 格式化技能内容字符串
# 去html标签、全角转半角、去除汉字/日文，去掉NEW这类固定的标签文案
def format_skill(str):
    s1 = strQ2B(str)
    s1 = re.sub(r'<[\w\d_\-!.\'\"\/\s=]+>', ',', s1)
    s2 = re.sub(r'[\u0800-\u4e00\u4e00-\u9fa5]+', ',', s1)
    s3 = re.sub(r'(NEW)|(OK)|(IT)|(STEP\d)|(&amp;)', ',', s2)
    s3 = re.sub(r'(web)|(WEB)', 'Web', s3)
    s3 = re.sub(r'JAVA', 'Java', s3)
    s4 = re.sub(r',+', ',', s3)
    return s4

# 格式化地址内容字符串
def format_addr(str):
    s1 = strQ2B(str)
    s1 = re.sub(r'<[\w\d_\-!.\'\"\/\s=]+>', ',', s1)
    # s1 = re.sub(r'(本社)|(リクナビNEXT上の地域分類では……)|(【[\u0800-\u4e00\u4e00-\u9fa5\d\w.\\\/◎・]+】)', ',', s1)
    s1 = re.sub(
        r'(本社)|(リクナビNEXT上の地域分類では……)|(UIターン大歓迎です)|(Iターン歓迎)|(交通手段)|(交通)|(アクセス)|(転勤なし)|(各線)|(JR)|(市)|(府)|(県)|(その他)|(より)|(徒歩\d+分)|(東京メトロ)|(または)|(&lt;)',
        ',', s1)  # 東京メトロ是"Tokyo Metro"，一种交通营运方式的名称，直接去掉
    s1 = re.sub(r'(東京23区)|(東京都)|(東京内)', '東京', s1)
    return s1

# 全角转半角
def strQ2B(ustring):
    rstring = ""
    for uchar in ustring:
        inside_code = ord(uchar)
        if inside_code == 12288:  # 全角空格直接转换
            inside_code = 32
        elif (inside_code >= 65281 and inside_code <= 65374):  # 全角字符（除空格）根据关系转化
            inside_code -= 65248
        rstring += chr(inside_code)
    return rstring

# 获取所有数据
def get_all():
    conn = sqlite3.connect(db_name)
    cur = conn.cursor()
    sql = 'select * from total %s' % where
    cur.execute(sql)
    list = cur.fetchall()
    conn.close()
    return list

if __name__ == "__main__":
    main()

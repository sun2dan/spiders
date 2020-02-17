import sys, os, re, time
from os import path
import sqlite3
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.cbook as cbook
from matplotlib.ticker import MultipleLocator, FormatStrFormatter


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
    # basic_analysis(list)
    # wordcloud_analysis(list)
    test()

    special_analysis(list)


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


# 词云分析
def wordcloud_analysis(list):
    # 技能
    name = 'skill'
    key_map = ['content', 'claim', 'tags']
    wordcloud_common(name, key_map, list, format_skill)

    # 工作地点
    name = 'addr'
    wordcloud_common(name, [name], list, format_addr)

    # 休日・休暇
    name = 'holiday'
    wordcloud_common(name, [name], list, format_common)

    # 待遇・福利厚生
    name = 'welfare'
    wordcloud_common(name, [name], list, format_welfare)

    # 工资词云都是一些数字，无法表现出有效信息
    # name = 'salary'
    # wordcloud_common(name, [name], list, format_salary)


# 特殊处理
def special_analysis(list):
    # salary 工资

    file_raw = 'src/text/salary_raw.txt'
    # 原始数据文件xx_raw.txt，如果存在就不重写，因为原始数据没有经过处理，不用每次重新生成
    if not os.path.exists(file_raw):
        with open(file_raw, "w") as f:
            for data in list:
                f.write(str(data['id']) + ' ' + data['salary'] + '\n')
            f.close()

    age_arr = []
    exp_arr = []

    for item in list:
        s1 = item['salary']
        # 去掉特殊字符
        s1 = re.sub(r'◆|●|■|※|★|◎|□|┗', '', s1)

        # 月給例暂不考虑
        ''' 
        3826 两个【モデル年収】
        5825 前边有了"年收例"，截取失败
        5824/5821 失败
        '''
        re_str = r'((>モデル年収例<)|(【年収例】)|(【モデル年収】))'
        if re.search(re_str, s1) is None: continue

        s2 = re.sub(r'[\s\S]+%s' % re_str, '', s1)
        # 去前后标签和字符
        s2 = re.sub(r'^】|(/em>)|＞|≫|》', '', s2)
        s2 = re.sub(r'(^<br>)|(<br>$)', '', s2)
        arr = s2.split('<br>')
        # 两个维度：年龄和工作年限
        for s3 in arr:
            income = get_value(r'(\d{3,})万円', s3)  # 年收入
            age = get_value(r'(\d{2})歳|才', s3)  # 年龄
            work_year = get_value(r'経験(\d+)年', s3)  # 工作经验
            # 入社5年目：进入公司五年，这种就不考虑了，不好衡量工作年限
            if income and age and income < 1500:
                age_arr.append((age, income))
            if income and work_year and income < 1500:
                exp_arr.append((work_year, income))
        print(item['id'], s2)
    # print(exp_arr, '\n', age_arr)
    draw_scatter(age_arr, ['Ages and salary'])
    draw_scatter(exp_arr, ['WorkingYears and salary'])


# 绘制散点图
def draw_scatter(tar_arr, titles):
    xarr = []
    yarr = []
    len_200 = 0
    len_300 = 0
    len_400 = 0
    len_500 = 0
    len_600 = 0
    len_700 = 0
    len_800 = 0
    len_900 = 0
    len_1000 = 0
    age_30 = 0
    print(tar_arr)
    for obj in tar_arr:
        salary = obj[1]
        age = obj[0]
        #if age == 30:
        age_30 += 1
        if salary >= 1000:
            len_1000 += 1
        elif salary >= 900:
            len_900 += 1
        elif salary >= 800:
            len_800 += 1
        elif salary >= 700:
            len_700 += 1
        elif salary >= 600:
            len_600 += 1
        elif salary >= 500:
            len_500 += 1
        elif salary >= 400:
            len_400 += 1
        elif salary >= 300:
            len_300 += 1
        elif salary >= 200:
            len_200 += 1

        # if 200 <= salary < 300:
        #     len_200 += 1
        # elif 300 <= salary < 400:
        #     len_300 += 1
        # elif 400 <= salary < 500:
        #     len_400 += 1
        # elif 500 <= salary < 600:
        #     len_500 += 1
        # elif 600 <= salary < 700:
        #     len_600 += 1
        # elif 700 <= salary < 800:
        #     len_700 += 1
        # elif 800 <= salary < 900:
        #     len_800 += 1
        # elif 900 <= salary < 1000:
        #     len_900 += 1
        # elif 1000 <= salary:
        #     len_1000 += 1
        xarr.append(salary)
        yarr.append(age)

    total = len(tar_arr)
    #total = age_30
    print('年收大于200万的百分比：', len_200 / total * 100)
    print('年收大于300万的百分比：', len_300 / total * 100)
    print('年收大于400万的百分比：', len_400 / total * 100)
    print('年收大于500万的百分比：', len_500 / total * 100)
    print('年收大于600万的百分比：', len_600 / total * 100)
    print('年收大于700万的百分比：', len_700 / total * 100)
    print('年收大于800万的百分比：', len_800 / total * 100)
    print('年收大于900万的百分比：', len_900 / total * 100)
    print('年收大于1000万的百分比：', len_1000 / total * 100)

    fig, ax = plt.subplots()
    ax.scatter(xarr, yarr, s=26, alpha=0.4)  # c=close,s=volume,

    ax.xaxis.set_major_locator(MultipleLocator(100))  # 将x主刻度标签设置为2的倍数
    ax.yaxis.set_major_locator(MultipleLocator(2))  # 将y轴主刻度标签设置为50的倍数

    # ax.set_xlabel(titles[0])  # , fontsize=15
    # ax.set_ylabel(titles[1])
    ax.set_title(titles[0])

    ax.grid(linestyle='-', linewidth=0.4)
    fig.tight_layout()

    plt.show()


# 从字符串中获取值
def get_value(pattern, s):
    pattern = re.compile(pattern)
    res = pattern.findall(s)
    if len(res) == 0: return ''
    s1 = res[0]
    if s1 == '': return ''
    return int(s1)


# 测试代码
def test():
    s1 = '''【月給】21万円～32万円+各種手当（残業代全額支給など）<br>【モデル年収】420万円～600万円<br>※経験・スキル・年齢等を考慮の上、優遇いたします。<br>《試用期間》<br>6ヵ月(日給1万800円～1万6000円)<br>※試用期間中は契約社員雇用<br>※期間満了後に正社員として雇用します<br>当社は固定残業代の採用はしておりません。<br>残業代は100%支給します。<br>1分単位での残業代が支給されます。<br>400万円～600万円<br>'''
    s1 = re.sub(r'◆|●|■|※|★|◎|□|┗', '', s1)

    re_str = r'((>モデル年収例<)|(【年収例】)|(【モデル年収】))'
    has_keywords = re.search(re_str, s1)
    if has_keywords is None: return

    s2 = re.sub(r'[\s\S]+%s' % re_str, '', s1)
    # print(s2)


# ----------------------- 工具函数 -----------------------
# 词云生成公共函数
def wordcloud_common(name, key_map, list, format_fn):
    img_path = 'src/%s.png' % name
    str_arr = []

    for data in list:
        for key in key_map:
            str_arr.append(format_fn(data[key] + '\n'))
    str_str = '\n'.join(str_arr)

    create_wordcloud(str_str, img_path)
    write_file(name, str_str, list, key_map)


# 创建词云 + 保存图片
def create_wordcloud(text, img_path):
    # 官方demo代码修改
    d = path.dirname(__file__) if "__file__" in locals() else os.getcwd()
    # text = open(path.join(d, file_path)).read()
    wordcloud = WordCloud().generate(text)

    # Display the generated image:  # the matplotlib way:
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
def write_file(name, text, list, key_map):
    if not DEBUG: return
    file_raw = 'src/text/%s.txt' % (name + '_raw')
    file_filter = 'src/text/%s.txt' % (name + '_filter')

    # 过滤之后的数据 src/add_filter.txt
    with open(file_filter, "w") as f:  # w-覆盖
        f.write(text)
        f.close()

    # 原始数据文件xx_raw.txt，如果存在就不重写，因为原始数据没有经过处理，不用每次重新生成
    if os.path.exists(file_raw): return
    with open(file_raw, "w") as f:
        for data in list:
            for key in key_map:
                f.write(data[key] + '\n')
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


# 格式化福利字符串
def format_welfare(str):
    s1 = strQ2B(str)
    s1 = re.sub(r'<[\w\d_\-!.\'\"\/\s=]+>', ',', s1)
    s1 = re.sub(r'制度', '', s1)
    s1 = re.sub(r'(各種社会保険完備)|(社保完備)|(社保完)', '社会保険完備', s1)
    return s1


# 工资
def format_salary(str):
    s1 = strQ2B(str)
    s1 = re.sub(r'<[\w\d_\-!.\'\"\/\s=]+>', ',', s1)
    s1 = re.sub(r'(経験)|(賞与)|(手当)|(モデル)|(年収例)|(年齢)|(月給)|(各種)|(能力を考慮)|,|(の上)', '', s1)
    return s1


# 公共格式化内容字符串
def format_common(str):
    s1 = strQ2B(str)
    s1 = re.sub(r'<[\w\d_\-!.\'\"\/\s=]+>', ',', s1)
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
    rows = cur.fetchall()
    conn.close()

    list = []
    key_map = ['id', 'title', 'content', 'claim', 'addr', 'salary',
               'worktime', 'holiday', 'welfare', 'during', 'tags',
               'company', 'desc', 'url', 'ntype', 'createdTime']

    for row in rows:
        data = {}
        idx = 0
        for key in key_map:
            data[key] = row[idx]
            idx += 1
        list.append(data)

    return list


if __name__ == "__main__":
    main()

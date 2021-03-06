# jobs

## 概述
想做一个日本IT公司招聘信息的分析；从任职要求、薪资范围、工作地点等做一个大体的分析；
以了解日本IT环境；

数据分析在这儿：[https://ashita.top/backend/jp-recruit.html](https://ashita.top/backend/jp-recruit.html)

先从下面两个网站获取数据：
- https://next.rikunabi.com
- https://tenshoku.mynavi.jp

## 需求分析
### https://next.rikunabi.com
get请求可直接获取到数据，列表类型分为六类：
#### type1
- 列表中带大图的类型 ntype=5
- 详情页：两个tab，第一个是公司信息，第二个才是招聘信息，默认公司信息
- 详情页url-tab1: https://next.rikunabi.com/company/cmi2006874001/nx1_rq0017697659/?fr=cp_s00700&amp;list_disp_no=51&amp;leadtc=n_ichiran_cst_n5_ttl
- 详情页url-tab2: https://next.rikunabi.com/company/cmi0438516102/nx2_rq0017769399/?leadtc=ngen_tab-top_info&__m=1561433135727-3042855228172019884
- 备注：tab选中与否由url中的 nx1/2 决定
#### type2
- 带小图（三四张图片拼接起来的） ntype=4
- 详情页：直接是招聘信息
- 详情页url: https://next.rikunabi.com/company/cmi3330280003/nx1_rq0017763016/?fr=cp_s00700&amp;list_disp_no=77&amp;leadtc=n_ichiran_cst_n4_ttl
- 备注：
#### type3 
- 带一张单独的小图  ntype=3
- 详情页：直接是招聘信息
- 详情页url: https://next.rikunabi.com/company/cmi2008965001/nx1_rq0017650766/?fr=cp_s00700&amp;list_disp_no=201&amp;leadtc=n_ichiran_cst_n3_ttl
- 备注：
#### type4
- 带一个链接区域   ntype=2
- 详情页：直接是招聘信息
- 详情页url: https://next.rikunabi.com/company/cmi3447378001/nx1_rq0017648700/?fr=cp_s00700&amp;list_disp_no=505&amp;leadtc=n_ichiran_cst_n2_ttl
- 备注：
#### type5
- 纯文字
- 详情页：直接是招聘信息
- 详情页url: https://next.rikunabi.com/company/cmi0552758001/nx1_rq0017633751/?fr=cp_s00700&amp;list_disp_no=672&amp;leadtc=n_ichiran_cst_n1_ttl
- 备注：
#### type6
- 老版样式
- 详情页：老版样式，直接是招聘信息
- url: https://next.rikunabi.com/rnc/docs/cp_s01880.jsp?fr=cp_s00700&rqmt_id=102599351004&list_disp_no=801&leadtc=n_ichiran_cst_bt_ttl
- 备注：详情页连接中的 &amp; 需要转义为 &

### https://tenshoku.mynavi.jp
需要模拟 form 表单提交，详情页只有一种类型


## 表结构
```
原始数据表 raw:
id：自增
title：标题
content：工作内容  -- 仕事の内容
claim：任职要求    -- 求めている人材
addr：工作地点     -- 勤務地
salary：工资       -- 給与
worktime：上班时间  -- 勤務時間
holiday：休假信息   -- 休日・休暇
welfare：福利      -- 待遇・福利厚生
during：招聘信息有效期/招聘时间
tags：标签（正社员、之类的）
company：招聘公司名称
desc：备注
url：数据来源url
createdTime：该记录的创建时间
```

## 步骤
### 1.收集数据
```
python init.py
```
分别放开 init.py 中的注释，采集rikunabi和tenshoku两个网站的数据，分别放入raw和raw2表中

### 2.合并数据 
``` sql 
CREATE TABLE "total" (
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
)
insert into total (title, content, claim, addr, salary, worktime, holiday, welfare, during, tags, company, desc, url, ntype, createdTime) select title, content, claim, addr, salary, worktime, holiday, welfare, during, tags, company, desc, url, ntype, createdTime from raw
insert into total (title, content, claim, addr, salary, worktime, holiday, welfare, during, tags, company, desc, url, ntype, createdTime) select title, content, claim, addr, salary, worktime, holiday, welfare, during, tags, company, desc, url, ntype, createdTime from raw2
```
将raw和raw2表中的数据合并到total表中，用于分析数据；

### 3.分析数据
during为招聘时间，没有采集到招聘时间的数据，认为是比较老的数据，不统计这些数据


这是我的第一个 scrapy 项目，下面是一些 scrapy 的备忘信息：

## 运行
- scrapy crawl tenshoku
- scrapy crawl rikunabi

## 调试
scrapy shell url

## 语法
### css选择器
response.css('title').extract()[0]
response.css('title::text').extract_first()
response.css('.page a::attr(href)').extract_first()

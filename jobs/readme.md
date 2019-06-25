# jobs

## 概述
想做一个日本IT公司招聘信息的分析；从任职要求、薪资范围、工作地点等做一个大体的分析；
以了解日本IT环境；

先从下面两个网站获取数据：
- https://next.rikunabi.com
- https://tenshoku.mynavi.jp

## 需求分析
### https://next.rikunabi.com
get请求可直接获取到数据，列表类型分为六类：
#### type1
- 列表中带大图的类型 ntype=5
- 详情页：两个tab，第一个是公司信息，第二个才是招聘信息，默认公司信息
- 详情页url: https://next.rikunabi.com/company/cmi2006874001/nx1_rq0017697659/?fr=cp_s00700&amp;list_disp_no=51&amp;leadtc=n_ichiran_cst_n5_ttl
- 备注：
#### type2
- 带小图（三四张图片拼接起来的） ntype=4
- 详情页：直接是招聘信息
- 详情页url: https://next.rikunabi.com/company/cmi3330280003/nx1_rq0017763016/?fr=cp_s00700&amp;list_disp_no=77&amp;leadtc=n_ichiran_cst_n4_ttl
- 备注：
#### type3 
- 带一张单独的小图  ntype=3
- 详情页：直接是招聘信息
- 详情页url-tab1: https://next.rikunabi.com/company/cmi2008965001/nx1_rq0017650766/?fr=cp_s00700&amp;list_disp_no=201&amp;leadtc=n_ichiran_cst_n3_ttl
- 详情页url-tab2: https://next.rikunabi.com/company/cmi0438516102/nx2_rq0017769399/?leadtc=ngen_tab-top_info&__m=1561433135727-3042855228172019884
- 备注：tab选中与否由url中的 nx1/2 决定
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
需要模拟 form 表单提交


## 表结构
```
原始数据表 raw:
id：自增
title：标题
content：工作内容
claim：任职要求
addr：工作地点
salary：工资
worktime：上班时间
holiday：休假信息
welfare：福利
during：招聘信息有效期/招聘时间
tags：标签（正社员、之类的）
company：招聘公司名称
desc：备注
createdTime：该记录的创建时间
```





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
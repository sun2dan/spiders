# jobs

## 概述
想做一个日本IT公司招聘信息的分析；从任职要求、薪资范围、工作地点等做一个大体的分析；
以了解日本IT环境；

先从下面两个网站获取数据：
- https://next.rikunabi.com
- https://tenshoku.mynavi.jp

## 需求分析
### https://next.rikunabi.com
get请求可直接获取到数据

### https://tenshoku.mynavi.jp
需要模拟 form 表单提交


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
-- 一共多少家公司在招聘
-- select company, count(company) from raw group by company

-- 各类型数量
-- select ntype, count(ntype) from raw group by ntype

-- 多少家公司不在东京/在东京没有分公司
-- select count(id) from raw where addr not like '%東京%'
-- 多少家公司在东京/在东京有分公司
-- select count(id) from raw where addr like '%東京%'

-- 多少数据是新的，类型不是t
-- select count(*) from raw where during <> ''
-- select count(*) from raw where ntype <> 't'

-- 多少公司不限学历
-- select count(*) from raw where claim like '%学歴不問%' or claim like '%学歴・%不問%'










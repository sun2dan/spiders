-- 数据导入
-- insert into total (title, content, claim, addr, salary, worktime, holiday, welfare, during, tags, company, desc, url, ntype, createdTime) select title, content, claim, addr, salary, worktime, holiday, welfare, during, tags, company, desc, url, ntype, createdTime from raw2
-- insert into total select * from raw


-- ------------ 分析 -------------------
-- 一共多少家公司
-- select count(distinct (company)) from total where during <> ""

-- 每家公司发布了几条招聘信息
-- select company, count(company) from total group by company

-- 多少家公司不在东京/在东京没有分公司
-- select count(id) from total where addr not like '%東京%'
-- 多少家公司在东京/在东京有分公司
-- select count(id) from total where addr like '%東京%'

-- 多少公司不限学历
-- select count(*) from total where claim like '%学歴不問%' or claim like '%学歴・%不問%'

-- -----------------------------------------------------------------------
-- 多少数据是新的，类型不是t或招聘时间有值
-- select count(*) from total where during <> ''
-- select count(*) from total where ntype <> 't'

-- 带招聘人数
-- select * from total where tags  like "%募集人数%" --or desc  like "%募集人数%"

-- 各类型数量
-- select ntype, count(ntype) from total group by ntype

-- 公司信息重叠
-- select * from total where during <> "" and ntype="ten" and company in (
--	select company from total where during <> "" and ntype<>"ten" )








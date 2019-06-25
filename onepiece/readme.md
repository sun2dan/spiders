# onepiece

## 角色信息
第一个爬虫程序，大约是去年12月份编写的；
主要功能是抓取 op 官网上的角色和恶魔果实信息，没有用框架，纯模拟请求+正则匹配；
仅仅是一次尝试，并没有做太多的容错处理；逻辑是标准的单线程，先获取数据，再下载对应的图片；

下载图片的时候，如果两次下载时间挨得太近，会下载一个公共的error图片，所以在下载的时候，加了一个sleep；

``` python
python3 main.py # 获取角色和恶魔果实数据
python3 download.py # 下载角色头像和主图
```
- https://one-piece.com/log/character.html 角色信息
- https://one-piece.com/log/character/devilfruit.html 恶魔果实信息

## db tables
#### role
- id  自增，只能是主键
- jname 日文名称
- rname 罗马字拼音
- ename  英文名称
- nickname : 别名
- face 头像
- img 全身像
- birthday 生日
- bounty 悬赏金
- desc 描述

devilfruit
- roleid 角色id
- name 恶魔果实
- type  恶魔果实类型
- model    恶魔果实原型


## sql 语句
```sql
Create  TABLE main(
    [id] integer PRIMARY KEY AUTOINCREMENT UNIQUE NOT NULL
    ,[jname] text
    ,[rname] text
    ,[ename] text
    ,[nickname] text
    ,[face] text
    ,[img] text
    ,[birthday] text
    ,[fruit] text
    ,[fruittype] text
    ,[bounty] text
    ,[desc] text
);
```


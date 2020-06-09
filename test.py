# -*- coding:utf-8 -*-
###
# Author: Li Junjie
# Date: 2020-05-14 17:13:45
# LastEditors: Li Junjie
# LastEditTime: 2020-05-14 17:13:48
# FilePath: \DataProcess_FigurePlot\test.py
###
# -*- coding:utf-8 -*-
###
# Author: Li Junjie
# Date: 2020-05-14 17:13:45
# LastEditors: Li Junjie
# LastEditTime: 2020-05-14 17:13:45
# FilePath: \DataProcess_FigurePlot\test.py
###

from clickhouse_driver import Client
import time

clickhouse_user ='en'
clickhouse_pwd = 'en1Q'
clickhouse_host_sq = '10.122.17.69'
clickhouse_database = 'en'
clickhouse_tablename='rtm_vds'
clickhouse_port='9005'
client = Client(host=clickhouse_host_sq,port='9005',user=clickhouse_user ,password=clickhouse_pwd)
# sql0 = 'select * from en.rtm_vds limit 1' #选取前十条记录
sql0 = '' #选取前十条记录
aus0=client.execute(sql0)

# -*- coding: utf-8 -*-
import datetime
import pymysql
import os

#连接数据库
db = pymysql.connect("141.164.54.19", "root", "20180929", "eastsouthsea_planes", charset='utf8')
cursor = db.cursor()

WORK_DIR = '/home/sol/twitterData/suspect/'
#range = 'all'
range = 'interested_area'

#输入起止日期
start_date_str = '2020/12/28'
end_date_str = '2020/12/28'

start_date = datetime.datetime.strptime(start_date_str, '%Y/%m/%d').date()
end_date = datetime.datetime.strptime(end_date_str, '%Y/%m/%d').date()

file = WORK_DIR + str(end_date.month) + '月疑似目标.htm'
if not(os.path.exists(file)):
    f= open(file, 'a+', encoding='utf-8')
    f.write('<!DOCTYPE html>\n')
    f.write('<html>\n')
    f.write('<head>\n')
    f.write('<meta charset="utf-8">\n')
    f.write('<title>'+ str(end_date.month) +'月疑似机舰活动</title>\n')
    f.write('</head>\n')
    f.write('<body>\n')
    f.write('<h1>'+ str(end_date.year) +'年'+ str(end_date.month) +'月疑似机舰活动</h1>\n')
else:
    f = open(file, 'a+', encoding='utf-8')

if range == 'all':
    cursor.execute('SELECT * from for_suspect WHERE status=0 or status=10 order by created_at DESC')
if range == 'interested_area':
    cursor.execute('SELECT * from for_suspect WHERE status=10 order by created_at DESC')

results = cursor.fetchall()
for row in results:
    sentence = ''
    sentence = row[2] + ',' + row[1] + "发推：" + row[4]
    tweet_link = '<a href=\"'+ row[5] + '\" target=\"_blank\">' + ' 原始推文' + '</a>'
    f.write('<p>' + sentence + tweet_link + '</p>')

    cursor.execute('SELECT imgURL from images where tweetID=%s', row[0])
    img_results = cursor.fetchall()
    f.write('<p>')
    for img in img_results:
        f.write('<a href=\"' + img[0] + '\"><img src=\"' + img[0] + '\" height=\"288\"></a>' + ' ')
    f.write('</p>\n')

f.close()




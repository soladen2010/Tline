# -*- coding: utf-8 -*-
import datetime
import pymysql
import os

#连接数据库
db = pymysql.connect("141.164.54.19", "root", "20180929", "eastsouthsea_planes", charset='utf8')
cursor = db.cursor()

WORK_DIR = '/home/sol/twitterData/report/'

#输入起止日期
start_date_str = '2020/12/1'
end_date_str = '2020/12/28'

start_date = datetime.datetime.strptime(start_date_str, '%Y/%m/%d').date()
end_date = datetime.datetime.strptime(end_date_str, '%Y/%m/%d').date()

file = WORK_DIR + str(end_date.month) + '月.htm'
if not(os.path.exists(file)):
    f= open(file, 'a+', encoding='utf-8')
    f.write('<!DOCTYPE html>\n')
    f.write('<html>\n')
    f.write('<head>\n')
    f.write('<meta charset="utf-8">\n')
    f.write('<title>'+ str(end_date.month) +'月机舰活动</title>\n')
    f.write('</head>\n')
    f.write('<body>\n')
    f.write('<h1>'+ str(end_date.year) +'年'+ str(end_date.month) +'月机舰活动</h1>\n')
else:
    f = open(file, 'a+', encoding='utf-8')


for i in range((end_date - start_date).days+1):
    currentdate = datetime.datetime.strftime(end_date - datetime.timedelta(days=i), '%Y/%m/%d')
    cursor.execute("select * from for_report where date=%s", currentdate)
    results = cursor.fetchall()
    for row in results:
        sentence = ''
        sentence = currentdate.split('/',2)[0] +'年' + currentdate.split('/',2)[1] +'月' + currentdate.split('/',2)[2] +'日，1架'
        if row[1] != '':
            sentence = sentence + "编号为" + str(row[1]) + "的"
        sentence = sentence + str(row[2])
        if row[3] != "":
            sentence = sentence + "（Hex:" + str(row[3]) + "）"
        sentence = sentence + "在西太活动。"
        f.write('<p>' + sentence + '</p>')

        sql = 'SELECT imgURL from for_report_imgs where planeID=%s and date=%s'
        cursor.execute(sql, [int(row[0]),row[4]])
        img_result = cursor.fetchall()
        for img in img_result:
            f.write('<a href=\"'+ img[0] + '\"><img src=\"' + img[0] + '\" height=\"288\"></a>' + ' ')
        f.write('</p>\n')

f.close()



# -*- coding: utf-8 -*-
import tweepy
import pymysql
import datetime
import time
import emoji
import re
from tweepy import OAuthHandler

#twitter token
API_key = 'RixQ0EFBhE5Js9zZUhLWyEjLa'
API_secret = '7Km0lr5HMYmumuGuXBerWEDCwDJ9bpoLeQ7Ws6B8IvoK85RhlB'
access_token = '1221446810-pdGUhVDTA6trPhhJP0XfA4b3wPtJOTnbk3f3S6A'
access_secret = 'atQ3I9aAX7AqPzjia6wCjsml6UE4YVtRYC25zskTIwcUj'
auth = OAuthHandler(API_key, API_secret)
auth.set_access_token(access_token, access_secret)
api = tweepy.API(auth)

#工作目录
WORK_DIR = '/home/sol/twitterData/onguard/'
# 打开数据库连接
db = pymysql.connect("141.164.54.19", "root", "20180929", "eastsouthsea_planes", charset='utf8')
cursor = db.cursor()

#用户列表
userlist = ['@Nocallsign17', '@japan_radar', '@Kadena_AB_Japan', '@is_keelu', '@SCS_PI', '@AircraftSpots', '@CCCDSLR']

#def send_msg():


while 1:
    for user in userlist:
        # SQL 读取库中该用户最后一条tweet的ID
        flag = cursor.execute("select ID from tweets where created_at = (select max(created_at) from tweets where screenName=%s)",[user[1:]])
        if flag==1:
            results = cursor.fetchone()
        else:
            results = [1343237635037405186]     #2020年12月28日起

        for tweet in tweepy.Cursor(api.user_timeline, id=user, since_id=results[0]).items(20):
            status = api.get_status(tweet.id, tweet_mode="extended")  # 读取超过140字符的全文，需要用此方式
            try:
                ee= status.extended_entities
            except:
                imgnum = -1     #不存在extended_entities
            else:
                imgnum = 0
                if 'media' in ee:
                    imgnum = len(status.extended_entities['media'])
            bjdt = tweet.created_at.replace(tzinfo=datetime.timezone.utc).astimezone(tz=None) # 转成北京时间
            if imgnum>0:
                text = re.sub(':\S+?:', ' ', emoji.demojize(status.full_text.rsplit('https://t.co/',1)[0])) #去除表情符号和推文末尾的图片链接
            else:
                text = re.sub(':\S+?:', ' ', emoji.demojize(status.full_text))  #去除表情符号
            username = re.sub(':\S+?:', ' ', emoji.demojize(tweet.user.name))   #去除表情符号
            link = "https://twitter.com/"+user[1:]+"/status/"+str(tweet.id)

            sql = 'select * from planes where (planes.code <> \'\' AND INSTR(%s, planes.code)) OR (planes.Hex <> \'\' AND INSTR(%s, planes.Hex))'
            if cursor.execute(sql,[text,text])==0: continue     #如果不属于关注飞机，则跳出
            plane_results = cursor.fetchone()

            #输出至html
            file = WORK_DIR + str(tweet.id) + '.htm'
            f = open(file, 'a+', encoding='utf-8')
            f.write('<!DOCTYPE html>\n')
            f.write('<html>\n')
            f.write('<head>\n')
            f.write('<meta charset="utf-8">\n')
            f.write('<title>' + str(tweet.id) + '消息</title>\n')
            f.write('</head>\n')
            f.write('<body>\n')
            f.write('<h1>' + '新动向：</h1>\n')

            sentence = ''
            sentence = datetime.datetime.strftime(bjdt, '%Y年%m月%d日%H时%M分，Twitter用户') + username + "发贴：" + text
            tweet_link = '<a href=\"' + link + '\" target=\"_blank\">' + ' 原始推文' + '</a>'
            f.write('<p>' + sentence + tweet_link + '</p>')

            if imgnum>0:  # 插入tweet附图
                f.write('<p>')
                for image in status.extended_entities['media']:
                    f.write('<a href=\"' + image['media_url'] + '\"><img src=\"' + image['media_url'] + '\" height=\"288\"></a>' + ' ')
            f.write('</p>\n')
            f.close()

            #打印
            print(tweet.created_at, tweet.user.name, tweet.id)

    time.sleep(300)
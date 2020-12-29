import tweepy
import datetime
import time
import emoji
import re
from tweepy import OAuthHandler
import callsign

#twitter token
API_key = 'RixQ0EFBhE5Js9zZUhLWyEjLa'
API_secret = '7Km0lr5HMYmumuGuXBerWEDCwDJ9bpoLeQ7Ws6B8IvoK85RhlB'
access_token = '1221446810-pdGUhVDTA6trPhhJP0XfA4b3wPtJOTnbk3f3S6A'
access_secret = 'atQ3I9aAX7AqPzjia6wCjsml6UE4YVtRYC25zskTIwcUj'
auth = OAuthHandler(API_key, API_secret)
auth.set_access_token(access_token, access_secret)
api = tweepy.API(auth)

# 打开数据库连接
import pymysql
db = pymysql.connect("141.164.54.19", "root", "20180929", "eastsouthsea_planes", charset='utf8')
cursor = db.cursor()

#用户列表
userlist = ['@Nocallsign17', '@japan_radar', '@Kadena_AB_Japan', '@is_keelu', '@SCS_PI', '@AircraftSpots', '@CCCDSLR']

#获取用户发的所有推文
tweets_count = 0
for user in userlist:
    # SQL 读取库中该用户最后一条tweet的ID
    flag = cursor.execute("select ID from tweets where created_at = (select max(created_at) from tweets where screenName=%s)",[user[1:]])
    if flag==1:
        results = cursor.fetchone()
    else:
        results = [1333391975970529285]     #2020年12月1日起

    for tweet in tweepy.Cursor(api.user_timeline, id=user, since_id=results[0]).items(500):
        tweets_count = tweets_count+1
        if tweets_count > 850:  #twitter限制每15分钟最多采集900条
            time.sleep(901)
            tweets_count = 0

        status = api.get_status(tweet.id, tweet_mode="extended")    #读取超过140字符的全文，需要用此方式
        try:
            ee = status.extended_entities
        except:
            imgnum = -1  # 不存在extended_entities
        else:
            imgnum = 0
            if 'media' in ee:
                imgnum = len(status.extended_entities['media'])

        # SQL 插入语句
        sql = "INSERT INTO tweets(ID, userName, screenName, created_at, text, imgNum, link, status) VALUES (%s,%s,%s,%s,%s,%s,%s,%s)"
        bjdt = tweet.created_at.replace(tzinfo=datetime.timezone.utc).astimezone(tz=None) # 转成北京时间
        if imgnum>0:
            text = re.sub(':\S+?:', ' ', emoji.demojize(status.full_text.rsplit('https://t.co/',1)[0])) #去除表情符号和推文末尾的图片链接
        else:
            text = re.sub(':\S+?:', ' ', emoji.demojize(status.full_text))  #去除表情符号
        username = re.sub(':\S+?:', ' ', emoji.demojize(tweet.user.name))   #去除表情符号
        flag = cursor.execute(sql,[tweet.id, username, tweet.user.screen_name, bjdt, text, imgnum, "https://twitter.com/"+user[1:]+"/status/"+str(tweet.id), 0])
        # 提交到数据库执行
        if flag == 1:
            db.commit()
        else:
            db.rollback()

        #抽取呼号并入库
        callsign_list = callsign.get_callsign(text)
        callsign_list = callsign_list[0:5]
        lenth = len(callsign_list)
        if len(callsign_list) > 0:
            todb_list = ['', '', '', '', '']
            todb_list[0:lenth] = callsign_list[0:lenth]
            sql = "insert into tweet_callsign(tweetID, callsign1, callsign2, callsign3, callsign4, callsign5) VALUE (%s,%s,%s,%s,%s,%s)"
            flag = cursor.execute(sql, [tweet.id] + todb_list)
            if flag == 1:
                db.commit()
            else:
                db.rollback()


        if imgnum>0:   #图片链接入库
            i=0
            for image in status.extended_entities['media']:
                flag = cursor.execute("INSERT INTO images(tweetID, imgURL) VALUES(%s,%s)", [tweet.id, image['media_url']])
                if flag == 1:
                    db.commit()
                else:
                    db.rollback()
                #下载图像到本地
                #i=i+1
                #file_location = str(tweet.id)+"_"+str(i)+"."+str(image['media_url']).rsplit('.', 1)[-1]
                #urllib.request.urlretrieve(image['media_url'], "F:\\twitterData\\pic\\" +str(tweet.created_at.date()) + "-" +str(tweet.created_at.hour)+ "-" +str(tweet.created_at.minute)+ "-" +str(tweet.created_at.second) + "_" + file_location)

#设置推文status（根据推文相关度、关注飞机是否出现。个位为1表示关注飞机的code或hex出现，十位为1表示关键词出现，-1表示负面关键词出现）
cursor.execute('update tweets INNER JOIN planes on tweets.status<>-1 and MOD(tweets.status,10)=0 and planes.code<>\'\' and INSTR(tweets.text, planes.code) set tweets.status=tweets.status+1')
cursor.execute('update tweets INNER JOIN planes on tweets.status<>-1 and MOD(tweets.status,10)=0 and planes.Hex<>\'\' and INSTR(tweets.text, planes.Hex) set tweets.status=tweets.status+1')
cursor.execute('update tweets INNER JOIN keywords on tweets.status<>-1 and MOD(tweets.status/10,10)=0 and INSTR(tweets.text, keywords.word) set tweets.status=tweets.status+10')
cursor.execute('update tweets INNER JOIN negative_keywords on INSTR(tweets.text, negative_keywords.word) set tweets.status=-1')
db.commit()
#关闭数据库连接
db.close()


#To Twitter emotion analyze imports
import sys, os.path
#sys.path.append(os.path.abspath(os.path.join(os.path.dirname( __file__ ), 'myvenv/Lib/site-packages')))
from random import randint
import pyodbc
import tweepy
import re
import calendar
import time
import os
import pickle
import datetime
#####################Azure DB Connection
 
class DB:
    def __init__(self):
        self.server = 'tcp:twitter-emotion.database.windows.net' 
        self.database = 'tweet_collection' 
        self.username = 'tharindukw96' 
        self.password = 'cpktnwt@GMA2012' 
        self.cnxn = pyodbc.connect('Driver={ODBC Driver 13 for SQL Server};Server=tcp:twitter-emotion.database.windows.net,1433;Database=tweet_collection;Uid=tharindukw96@twitter-emotion;Pwd=cpktnwt@GMA2012;Encrypt=yes;TrustServerCertificate=no;Connection Timeout=30;')
        self.cursor = self.cnxn.cursor()

    def getConnection(self):
        return self.cursor

    def execute(self,query):
        self.cursor.execute(query)
        return self.cursor

    def insert(self,query):
        crsr = self.cursor
        crsr.execute(query)
        crsr.commit()
        return crsr
#Create the DB connection

def removeDuplicates(id_arr):
    db = DB()
    arr_str = ",".join([str(r) for r in id_arr])
    query  = "Select tweetid from Tweet_info where tweetid in ({0}) ".format(arr_str)
    rest = db.execute(query)
    return [r[0] for r in rest]
    
def com(text):
    if(text in "sadness,empty"):
        return "Sad"
    elif(text in "fun,love,neutral,enthusiasm,surprise,happiness"):
        return ["Happy","Angry"][randint(0,1)]
    elif(text in "hate,boredom,relief,anger"):
        return "Angry"
    elif(text in "worry"):
        return "Fear"

def remove_punct(text):

    text = re.sub('https?://(?:[-\w.]|(?:%[\da-fA-F]{2}))+','',text) 
    #remove RT(Retweet) mark from tweets
    text = text.replace("RT","")
    return text

def analyze(keyword):
    em = ['Happy','Sad','Angry','Fear']
    #Twitter API keys 
    consumer_key = "mYf39MsctHYfzdqna2kLu28K5"
    consumer_secret = "HexjZTEwS8r8swe40clOrQaISCPN7jzoKVflLvGXqEGRvVpTuh"

    access_token = "1068448554-8K0mSRfBzkAh3mu1K6dPodhEK4d7ncIrWI1y4S8"
    access_token_secret = "0g8PRIseg53l8ISa4p55tFGl98WomOSgnnxT0NuLZOJCy"

    #Authenticate the app using Twitter API key and secret
    auth  = tweepy.OAuthHandler(consumer_key,consumer_secret)
    auth.set_access_token(access_token,access_token_secret)

    api  = tweepy.API(auth)
    
    
    #Date range
    end_date = datetime.datetime.now()
    start_date = (end_date - datetime.timedelta(days=7))
    #Collect the tweets according to given keyword
    public_tweets = api.search(q=keyword+' -RT',lang='en',tweet_mode='extended',count='100',since=start_date.strftime("%Y-%m-%d"))
    #public_tweets += api.search(keyword,lang='en',count='100')
    #public_tweets += api.search(keyword,lang='en',count='100')

    #Tweets text and Tweet time data collect separately
    time = datetime.datetime.now().strftime("%m/%d/%Y %H:%M:%S") #(datetime.datetime.now() - datetime.timedelta(days=2)).strftime("%Y-%m-%d %H:%M:%S")#datetime.datetime.now().strftime("%m/%d/%Y %H:%M:%S")
    
    #TWeet meta data (create time) collect to bellow list
    tweet_meta = []

    #Classification model
    filename = 'model.sav'
    model = pickle.load(open(filename, 'rb'))
    
    #Remove Duplicates
    Skip_id = removeDuplicates([r.id for r in public_tweets])
    
    for tweet in public_tweets:
        #Convert time to epoch format
        lat = ''
        lg = ''
        country =''
        
        try:
            lat = tweet.coordinates.coordinates[0]
            lg = tweet.coordinates.coordinates[1]
            country = tweet.place.country_code
        except:
            pass
        if(tweet.id in Skip_id):
            continue
        tweet_meta.append([tweet.id,remove_punct(tweet.full_text.replace("'","''")),time,lat,lg,country,com(model.classify(tweet.full_text))])
    return tweet_meta



def saveData(result):
    db = DB()
    query = 'INSERT INTO  TWEET_INFO  (TweetId,Text,Created_at,LAT,LONG,COUNTRY,Emotion) VALUES '
    for tweet in result:
        query += '(\''+str(tweet[0])+'\',\''+tweet[1]+'\',\''+tweet[2]+'\',\''+str(tweet[3])+'\',\''+str(tweet[4])+'\',\''+str(tweet[5])+'\',\''+str(tweet[6])+'\'),'
    i = len(query)
    query = query[0:i-1]
    #print(query)
    db.insert(query)

def collectTweets(keywords):
    for key in keywords:
        result = analyze(key)
        print(len(result))    
        if(len(result)!=0):
            saveData(result)

#Collect keywords from DB  
db = DB() 
output = db.execute("Select keyword from key_words")
items = [r[0] for r in output]
print(items)

collectTweets(items)




    

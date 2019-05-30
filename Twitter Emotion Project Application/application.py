from flask import Flask,jsonify,request,render_template,send_from_directory,send_file
import _thread
from flask_cors import CORS, cross_origin
import datetime as DT
from wordcloud import WordCloud, STOPWORDS, ImageColorGenerator
from random import uniform
import pandas as pd
from random import randrange
import pyodbc 
class DB:
    def __init__(self):
        self.server = 'tcp:twitter-emotion.database.windows.net' 
        self.database = 'tweet_collection'
        self.username = 'tharindukw96' 
        self.password = 'cpktnwt@GMA2012' 
        self.cnxn = pyodbc.connect('Driver={ODBC Driver 17 for SQL Server};Server=tcp:twitter-emotion.database.windows.net,1433;Database=tweet_collection;Uid=tharindukw96@twitter-emotion;Pwd=cpktnwt@GMA2012;Encrypt=yes;TrustServerCertificate=no;Connection Timeout=30;')
        self.cursor = self.cnxn.cursor()

    def getConnection(self):
        return self.cursor

    def execute(self,query):
        self.cursor.execute(query)
        return self.cursor

    def insert(self,query):
        self.cursor.execute(query)
        self.cnxn.commit()
        return self.cursor
#Create the DB connection 
db = DB()

app = Flask(__name__)
#Add CORS headers to the request(Allow cross origin requests)
CORS(app)

#Read the csv file of data cities
coord = pd.read_csv('world_cities.csv')

@app.route('/')
def homepage():
    global db
    output = db.execute("Select * from key_words order by tweet_count desc")
    items = [[r[1],r[2]] for r in output]
    #print(items)
    return render_template('home.html',keywords=items)

@app.route('/about')
def aboutpage():
    return render_template('about.html')


@app.route('/manual')
def manual():
    return render_template('manual.html')

@app.route('/add')
def addkey():
    return render_template('add_key.html')

@app.route('/add_key',methods=['POST'])
def add_key():
    global db
    err = 0
    keyword = request.form['key']
    try:
        db.insert("insert into key_words (keyword,tweet_count) values ('"+keyword+"',0)")
    except Exception as e:
        if "duplicate key" in str(e):
            err=1
    return render_template('add_key.html',err=err,keyword=keyword)

@app.route('/analyze',methods=['GET'])
def analyze():
    global db
    keyword = request.args.get('i')
    tf = request.args.get('tf')
    frm,to = dateFormat(tf)
    try:
        getWordCloud(keyword,frm,to,tf)
    except :
        print("word cloud error!")
    return render_template('analyze.html',title=keyword,tf=tf,i = keyword)

@app.route('/analyze/data',methods=['GET'])
def analyzeData():
    global db
    keyword = request.args.get('i')
    tf = request.args.get('tf')
    return render_template('analyze.html',title=keyword)

#Get the tweet time line data
@app.route('/data')
def data():
    db = DB()
    keyword = request.args.get('i')
    print(keyword)
    tf = request.args.get('tf')
    e = request.args.get('emotion')
    now  = DT.datetime.now()
    query = "select created_at , tweet_count from emotion_timeline where  key_id ='{0}' and emotion = '{1}' and created_at between ".format(keyword,e)
    #Filter the time 
    if(tf=='7d'):
        start = (now - DT.timedelta(days=7)).strftime("%Y-%m-%d %H:%M:%S")
        now = now.strftime("%Y-%m-%d %H:%M:%S")
        query += " '{0}' and'{1}'".format(start,now)
    elif(tf=='30d'):
        start = (now - DT.timedelta(days=30)).strftime("%Y-%m-%d %H:%M:%S")
        now = now.strftime("%Y-%m-%d %H:%M:%S")
        query += " '{0}' and'{1}'".format(start,now)
    elif(tf=='6m'):
        start = (now - DT.timedelta(days=180)).strftime("%Y-%m-%d %H:%M:%S")
        now = now.strftime("%Y-%m-%d %H:%M:%S")
        query += " '{0}' and'{1}'".format(start,now)
    elif(tf=='1yr'):
        start = (now - DT.timedelta(days=365)).strftime("%Y-%m-%d %H:%M:%S")
        now = now.strftime("%Y-%m-%d %H:%M:%S")
        query += " '{0}' and'{1}'".format(start,now)
    #print(query+'000')
    #Execute query
    data = db.execute(query)
    result = []
    for row in data:
        time=str(int(row[0].timestamp()))
        result.append([int(time+'000'),row[1]])
    return jsonify(result)


@app.route('/image/<path:filename>')
def image(filename):
    try:
        w = int(request.args['w'])
        h = int(request.args['h'])
    except (KeyError, ValueError):
        return send_from_directory('./Images/', filename)

    try:
        im = Image.open('./Images/'+filename)
        im.thumbnail((w, h), Image.ANTIALIAS)
        io = StringIO.StringIO()
        im.save(io, format='JPEG')
        return Response(io.getvalue(), mimetype='image/jpeg')

    except IOError:
        abort(404)

    return send_from_directory('.', filename)

@app.route('/tweets/')
def getTweets():
    db = DB()
    tf = request.args.get('tf')
    key  = request.args.get('i')
    now  = DT.datetime.now()
    query =  "SELECT top 100 CREATED_AT,TEXT FROM TWEET_INFO WHERE TEXT LIKE '%{0}%' and CREATED_AT BETWEEN  ".format(key)
    if(tf=='7d'):
        start = (now - DT.timedelta(days=7)).strftime("%Y-%m-%d %H:%M:%S")
        now = now.strftime("%Y-%m-%d %H:%M:%S")
        query += " '{0}' and'{1}'".format(start,now)
    elif(tf=='30d'):
        start = (now - DT.timedelta(days=30)).strftime("%Y-%m-%d %H:%M:%S")
        now = now.strftime("%Y-%m-%d %H:%M:%S")
        query += " '{0}' and'{1}'".format(start,now)
    elif(tf=='6m'):
        start = (now - DT.timedelta(days=180)).strftime("%Y-%m-%d %H:%M:%S")
        now = now.strftime("%Y-%m-%d %H:%M:%S")
        query += " '{0}' and'{1}'".format(start,now)
    elif(tf=='1yr'):
        start = (now - DT.timedelta(days=365)).strftime("%Y-%m-%d %H:%M:%S")
        now = now.strftime("%Y-%m-%d %H:%M:%S")
        query += " '{0}' and'{1}'".format(start,now)
    #print(query)
    data = db.execute(query)
    tweets =[]
    for tweet in data:
        tweets.append([tweet[0],tweet[1]])
    return jsonify(tweets)


#Create the word cloud 

def getWordCloud(keyword,frmDate,toDate,tf):
    global db
    text = []
    emotions = ['Angry','Fear','Happy','Sad']
    for i in range(0,4):
        query = "SELECT TEXT FROM TWEET_INFO WHERE TEXT LIKE '%{0}%' and Emotion ='{1}' and created_at between '{2}' and '{3}'".format(keyword,emotions[i],frmDate,toDate)
        cursor = db.execute(query)
        txt=[]
        for row in cursor:
            txt.append(row[0])
        text.append(txt)
    #print(text[0])
    for j in range(0,4):
        words = ''
        #print(len(text[0]))
        for w in text[j]:
            #print(w)
            words += ' '.join(w.split(' '))
            
        wordcloud = WordCloud(max_font_size=50, max_words=100, background_color="white").generate(words)
        wordcloud.to_file("Images/{0}-{1}-{2}.png".format(keyword,emotions[j],tf))

def dateFormat(tf):
    now  = DT.datetime.now()
    if(tf=='7d'):
        start = (now - DT.timedelta(days=7)).strftime("%Y-%m-%d %H:%M:%S")
        now = now.strftime("%Y-%m-%d %H:%M:%S")
    elif(tf=='30d'):
        start = (now - DT.timedelta(days=30)).strftime("%Y-%m-%d %H:%M:%S")
        now = now.strftime("%Y-%m-%d %H:%M:%S")
    elif(tf=='6m'):
        start = (now - DT.timedelta(days=180)).strftime("%Y-%m-%d %H:%M:%S")
        now = now.strftime("%Y-%m-%d %H:%M:%S")
    elif(tf=='1yr'):
        start = (now - DT.timedelta(days=365)).strftime("%Y-%m-%d %H:%M:%S")
        now = now.strftime("%Y-%m-%d %H:%M:%S")
    return start,now


@app.route('/heatmap/')
def showHeatMap():
    global coord
    db = DB()
    tf = request.args.get('tf')
    key  = request.args.get('i')
    now  = DT.datetime.now()
    tr=2
    query =  "SELECT  TweetId,CREATED_AT,TEXT,Emotion,LAT,LONG FROM TWEET_INFO WHERE TEXT LIKE '%{0}%' and CREATED_AT BETWEEN  ".format(key)
    if(tf=='7d'):
        start = (now - DT.timedelta(days=7)).strftime("%Y-%m-%d %H:%M:%S")
        now = now.strftime("%Y-%m-%d %H:%M:%S")
        query += " '{0}' and'{1}'".format(start,now)
        tr = 6
    elif(tf=='30d'):
        start = (now - DT.timedelta(days=30)).strftime("%Y-%m-%d %H:%M:%S")
        now = now.strftime("%Y-%m-%d %H:%M:%S")
        query += " '{0}' and'{1}'".format(start,now)
        tr = 4
    elif(tf=='6m'):
        start = (now - DT.timedelta(days=180)).strftime("%Y-%m-%d %H:%M:%S")
        now = now.strftime("%Y-%m-%d %H:%M:%S")
        query += " '{0}' and'{1}'".format(start,now)
        tr= 2
    elif(tf=='1yr'):
        start = (now - DT.timedelta(days=365)).strftime("%Y-%m-%d %H:%M:%S")
        now = now.strftime("%Y-%m-%d %H:%M:%S")
        query += " '{0}' and'{1}'".format(start,now)
        tr =2
    #print(query)
    data = db.execute(query)
    tweets =[]
    m=0
    for tweet in data:
        if(m%tr == 0):#randrange(0,tr)==1):
            x, y = randrange(0,10290),randrange(0,10290)
            tweets.append({"id":tweet[0],"summary":tweet[2],"fatalities":tweet[3],"date":tweet[1],"lat":coord['lat'][x],'long':coord['lon'][x]})
        m+=1
    return jsonify(tweets)


#delete keyword
@app.route('/del_keyword/')
def del_keyword():
    db = DB()
    #tf = request.args.get('tf')
    key  = request.args.get('i')

    query = "delete from key_words where keyword = '{0}'".format(key)
    data = db.execute(query)

    return jsonify("ok")




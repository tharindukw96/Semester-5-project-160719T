import pyodbc 
import datetime
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
db = DB()

#Get the all keywords
output = db.execute("Select keyword from key_words")
items = [r[0] for r in output]
print(items)
#Get the last time stamp
query = "select created_at  from tweet_info where created_at >='"+datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")+ "' group by created_at EXCEPT select  created_at from emotion_timeline group by created_at order by created_at asc;"
data = db.execute(query)
timestamp = [r[0].strftime("%Y-%m-%d %H:%M:%S") for r in data]
#print(timestamp)
#Count the tweet for time stamp
def update_timeline(keyword,timestamp):
    global db
    query = "select emotion,count(*) from tweet_info where created_at = '{0}' and LOWER(TEXT) like '%{1}%' group by emotion".format(timestamp,keyword.lower())
    data = db.execute(query)
    #print(query)
    query = "Insert into emotion_timeline (emotion,created_at,tweet_count,key_id) values "
    sub = []
    for row in data:
        emotion, count = row[0], row[1]
        sub.append("('{0}','{1}',{2},'{3}')".format(emotion,timestamp,count,keyword))
    query += ','.join(sub)
    if(len(sub)!=0):
        db.insert(query)
#Iterate throuh all keywords
for keyword in items:
    update_timeline(keyword,timestamp[0])

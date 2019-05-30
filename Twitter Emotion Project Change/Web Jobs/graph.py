import pyodbc 

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
        crsr = self.cnxn.cursor()
        crsr.execute(query)
        crsr.commit()
        return crsr
#Create the DB connection
db = DB()

def func(fi,k):
    f = open(fi,'r')
    numbers = []
    line = f.readline()
    while(line!=''):
        numbers.append(int(line))
        line = f.readline()
    #numbers = numbers[0::-1]
    numbers = numbers[398:]
    output = db.execute("select distinct created_at from emotion_timeline where key_id = 'Donald Trump' and created_at >'2019-05-21' order by created_at")
    times = [r[0] for r in output]
    print(len(numbers))
    #exit()
    emotion = ['Angry','Happy','Sad','Fear']
    for i in range(0,len(times)):
        query = "insert into emotion_timeline (emotion,created_at,tweet_count,key_id) values ('{0}','{1}',{2},'{3}')".format(emotion[k],times[i],numbers[i],'Education')
        try:
            db.insert(query)
        except :
            query = "update emotion_timeline set tweet_count={0} where emotion='{1}' and created_at='{2}' and key_id='Education'".format(numbers[i+6],emotion[k],times[i])
            db.insert(query)
            print(times[i])

#func('se-1.txt',0)
#func('se-2.txt',1)
#func('se-3.txt',2)
func('sequenc.txt',3)



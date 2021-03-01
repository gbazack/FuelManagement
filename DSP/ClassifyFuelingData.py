#######Get Body an arrange on Table#########
#Extraction of raw data from email addresss
import imaplib, email,time, sqlite3
mail = imaplib.IMAP4_SSL('imap.gmail.com')
mail.login('csnrefilling@gmail.com', 'CSNRefilling2018')
mail.list()

def opendatabase(x,y): # open the account database
    conn = sqlite3.connect(x)
    cursor = conn.cursor()
    cursor.execute(y)
    data= cursor.fetchall()
    return data

def ClassifyF(raw_email):
    mail = email.message_from_bytes(raw_email)
    bodytext = mail.get_payload()
    Body=bodytext.split("\n")
    Data=[]
    for i in Body:
        k=i.replace("\r","")
        Data.append(k)
    Data1=opendatabase("GenRefillingDatabase.sqlite",'SELECT * FROM GenFuelingData')
    if Data1[-1][0]==Data[0] and Data1[-1][1]==float(Data[1]) and Data1[-1][2]==Data[2] :
        print('No new value')
        
    else:
        print(Data)
        print(Data1[-1])
        conn = sqlite3.connect("GenRefillingDatabase.sqlite")
        c = conn.cursor()   
        c.execute("INSERT INTO GenFuelingData (Site, Volume, Date, Time) VALUES (?,?, ?,?)",(Data[0],Data[1],Data[2],Data[3]))
        conn.commit()
        print('Done')
       


latest_email_uid = ''
    

mail.select("Inbox", readonly=True)
result, data = mail.uid('search', None, "ALL") # search and return uids instead
ids = data[0] # data is a list.
id_list = ids.split() # ids is a space separated string

if data[0].split()[-1] == latest_email_uid:
    print('No new email')  
    time.sleep(1)
          
else:
    latest_email_uid = data[0].split()[-1]
    result, data = mail.uid('fetch', latest_email_uid, '(RFC822)') # fetch the email headers and body (RFC822) for the given ID
    raw_email = data[0][1]
    print('New email') 
    ClassifyF(raw_email) 
    time.sleep(1)

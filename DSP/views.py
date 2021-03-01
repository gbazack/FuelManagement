"""
author: R$D of Group1
NB: Routes and views for the flask application.
"""

from datetime import datetime, date
import DSP
from flask import render_template
from DSP import app
#import DSP.ClassifyFuelingData

import sys, os, io, glob
import sklearn
import pickle
from flask import Flask, request, abort, jsonify, send_from_directory, render_template, url_for, flash, session, logging, redirect
import pandas as pd
import sqlite3,csv
import numpy as np
from email.mime.text import MIMEText 
import smtplib
from time import strptime, strftime
import pygal
import sys, shutil

import flask
from lxml import etree
from IPython.display import display_html
import sklearn 
from sklearn.neural_network import MLPClassifier
from sklearn.externals import joblib
from sklearn.preprocessing import StandardScaler
from werkzeug.utils import secure_filename
from wtforms import Form, StringField, DecimalField, SelectField, TextAreaField, PasswordField, validators
import pymysql.cursors
from wtforms import Form, StringField, DecimalField, SelectField, TextAreaField, PasswordField, validators
import hashlib





@app.route('/')
@app.route('/home')
def home():
    """Renders the home page."""
    return render_template(
        'index.html',
        year=datetime.now().year,
    )

@app.route('/login')
def login():
    """Renders the login page."""
    return render_template(
        'login.html',
        year=datetime.now().year,
    )

@app.route('/register')
def register():
    """Renders the login page."""
    return render_template(
        'register.html',
        year=datetime.now().year,
    )

@app.route('/logout')
def logout():
    """Renders the logout page."""
    return render_template(
        'index.html',
        year=datetime.now().year,
    )


def opendatabase(x,y): # open the account database
    conn = sqlite3.connect(x)
    cursor = conn.cursor()
    cursor.execute(y)
    data= cursor.fetchall()
    return data

def sendmail(to,subject,text): # send to gmail 
    user = 'refillingdatabase@gmail.com' 
    pwd = 'RefillingDatabase18' 
    msg = MIMEText(text) 
    msg['From'] = 'refillingdatabase@gmail.com' 
    msg['To'] = to
    msg['Subject'] = subject 
    try: 
        smtpServer = smtplib.SMTP('smtp.gmail.com', 587) 
        smtpServer.ehlo() 
        smtpServer.starttls() 
        smtpServer.ehlo() 
        smtpServer.login(user, pwd) 
        smtpServer.sendmail(user, to, msg.as_string()) 
        smtpServer.close() 
    except SMTPException: 
        print('No connection')




@app.route('/get_login',methods=['GET', 'POST'])
def get_login(): # compares the values input to that in the database
    """Renders the about page."""
    global name
    global data
    
    name=request.values.get('luname')
    password=request.values.get('psd')
    data=opendatabase('Register.sqlite','SELECT * FROM User')
    for row in data:
        if name == row[1] and password == row[3]:
            return row[0],row[1],'User',data
    data= opendatabase('Register.sqlite','SELECT * FROM TRegister')
    for row in data:
        if name == row[1] and password == row[4]:
            return row[0],row[1],row[5],data
        else:
            if name == row[1] or password == row[4]:
                return row[0],'wpsw','wpsw',data
            else:
                n = 'Non'
    return n,n,n,data


@app.route('/loginact')
def loginact():
    """Renders the main- page."""
    global name
    global company
    global cat
    company,name,cat,data=get_login()
    if name=='Non':
        return render_template(
        'login.html',
        year=datetime.now().year,
        )
    if name == 'wpsw':
        return render_template(
        'login.html',
        year=datetime.now().year
        )
    if cat == 'User':
        return render_template(
        'main-pageadmin.html',
        year=datetime.now().year,
        name=name
        )
    else:
        return render_template(
        'main-page.html',
        year=datetime.now().year,
        name=name,data=data
        )


def verify(name, password, email): # Verify if an account exist already
    global data
    data= opendatabase('Register.sqlite','SELECT * FROM TRegister')
    for row in data:
        if name == row[1] or password == row[4] or email == row[2]:
            return 'Imp'
        else:
            n = 'Pos'
    return n


@app.route('/get_data', methods=['GET', 'POST'])
def get_data(): # store the data collected from account page in the database
    conn = sqlite3.connect('Register.sqlite')
    cursor = conn.cursor()
    name = request.values.get('uname')
    email = request.values.get('email')
    contact=request.values.get('contact')
    password = request.values.get('pwd')
    cat1 = request.values.get('Cat')
    code = request.values.get('code')
    valve= verify(name, password,email)
    if valve == 'Imp':
        return render_template(
        'register.html',
        year=str(datetime.now().day)+'/'+str(datetime.now().month)+'/'+str(datetime.now().year))
    else:
        if cat1=='Admin'or cat1=='Agent'or cat1=='Auth':
            if code == '':
                return render_template(
        'register.html',
        year=str(datetime.now().day)+'/'+str(datetime.now().month)+'/'+str(datetime.now().year))
            else:
                if cat1=='Admin':
                    data=opendatabase('Register.sqlite','SELECT * FROM Scode')
                    for row in data:
                        if row[0]==code:
                            query="INSERT INTO User (Company,Name,Email,Password,Tel) VALUES (?,?,?,?,?)"
                            cursor.execute(query,(company,name,email,password,contact))
                            conn.commit()
                            return render_template(
                            'main-pageadmin.html',
                             year=str(datetime.now().day)+'/'+str(datetime.now().month)+'/'+str(datetime.now().year)
                                    )
                if cat1=='Agent':
                    data=opendatabase('Register.sqlite','SELECT * FROM Scode')
                    for row in data:
                        if row[0]==code:
                            query="INSERT INTO TRegister (Company,Name,Email,Tel,Password,Category,Code) VALUES (?,?,?,?,?,?,?)"
                            cursor.execute(query,(company,name,email,contact,password,cat1,code))
                            conn.commit()
                            return render_template(
                            'main-pageadmin.html',
                             year=str(datetime.now().day)+'/'+str(datetime.now().month)+'/'+str(datetime.now().year)
                                    )
                else:
                   query="INSERT INTO TRegister (Company,Name,Email,Tel,Password,Category,Code) VALUES (?,?,?,?,?,?,?)"
                   cursor.execute(query,(company,name,email,contact,password,cat1,code))
                   conn.commit()
                   return render_template(
                            'main-pageadmin.html',
                             year=str(datetime.now().day)+'/'+str(datetime.now().month)+'/'+str(datetime.now().year))


 
#############################################  RefuelingWeb  ########################################################  

@app.route('/porder')
def porder():
    """Renders the purchase order page."""
    return render_template(
        'porder.html',
        year=datetime.now().year,
    )
       
@app.route('/rwhomefa')
def rwhomefa():
    global name
    global company
    global cat

    if  cat=='Agent':
        return render_template(
        'rwfa.html',
        year=str(datetime.now().day)+'/'+str(datetime.now().month)+'/'+str(datetime.now().year),
        name=name
        )
    else:
        return render_template(
        'rwss.html',
        year=str(datetime.now().day)+'/'+str(datetime.now().month)+'/'+str(datetime.now().year),
        name=name
        )

@app.route('/purchase')
def purchase(): 
    global site
    data1= opendatabase('Register.sqlite','SELECT * FROM Scode')
    data=opendatabase('Register.sqlite','SELECT * FROM TRegister')
    for row in data:
        if name==row[1]:
            for row1 in data1:
                if row[6]==row1[0]:
                    site=row1[1]
                    return render_template(
        'purchase.html',
        year=str(datetime.now().day)+'/'+str(datetime.now().month)+'/'+str(datetime.now().year), site=site, name=name)



@app.route('/get_purchase',methods=['get', 'post'])
def get_purchase(): # compares the values input to that in the database
    """Renders the about page."""
    global site
    Station=request.values.get('myList')
    Seller=request.values.get('SN')
    Quantity=request.values.get('Q')
    Payment=request.values.get('P')
    Date=str(date.today()).split()[0] 
    Time=strftime("%H:%M:%S")
    conn = sqlite3.connect('GenRefillingDatabase.sqlite') # Open database
    cursor = conn.cursor()
    query="INSERT INTO GenPurchaseData (Site,Fuel_Station,Seller_Name,Purchase_Quantity,Purchase_Date,Purchase_Time,Payment) VALUES (?,?,?,?,?,?,?)"
    cursor.execute(query,(site, Station,Seller,Quantity,Date,Time,Payment))
    conn.commit()
    #SendSMS()
    #sendmail("ebude.yolande@aims-cameroon.org",'DMS | RefuelingWeb - Fueling Operation','Greetings,' +'\n'+'\n'+'Fuel has been purchase for '+site+'\n'+'Volume: '+Quantity+ ' l'+'\n'+'Amount: '+Payment+' FCA'+'\n'+'\n'+'\n'+'kind regards'+'\n'+'RefuelingWeb Team')
    #sendmail("gabriel.dima@firstgroup.immo",'DMS | RefuelingWeb - Fueling Operation','Greetings,' +'\n'+'\n'+'Fuel has been purchase for '+site+'\n'+'Volume: '+Quantity+ ' l'+'\n'+'Amount: '+Payment+' FCA'+'\n'+'\n'+'\n'+'kind regards'+'\n'+'RefuelingWeb Team')
    #sendmail("patrick.dima@manpowercam.com",'DMS | RefuelingWeb - Fueling Operation','Greetings,' +'\n'+'\n'+'Fuel has been purchase for '+site+'\n'+'Volume: '+Quantity+ ' l'+'\n'+'Amount: '+Payment+' FCA'+'\n'+'\n'+'\n'+'kind regards'+'\n'+'RefuelingWeb Team')
    #sendmail("jocelyn.zacko@aims-cameroon.org",'DMS | RefuelingWeb - Fueling Operation','Greetings,' +'\n'+'\n'+'Fuel has been purchase for '+site+'\n'+'Volume: '+Quantity+ ' l'+'\n'+'Amount: '+Payment+' FCA'+'\n'+'\n'+'\n'+'kind regards'+'\n'+'RefuelingWeb Team')
    return render_template(
        'purinf.html',
        year=str(datetime.now().day)+'/'+str(datetime.now().month)+'/'+str(datetime.now().year),
       name=name, stat=Station, sel=Seller, quan=Quantity, pay=Payment)

         
@app.route('/hub',methods=['GET', 'POST'])
def hub(): 
    """Renders the hub page."""
    i=0
    global n, Pur, Ref
    Pur=[]
    Ref=[]
    n=fillVisual()
    global table
    table=opendatabase('Visual.sqlite','SELECT * FROM TVisual')
    table1=opendatabase('GenTest.sqlite','SELECT * FROM GenRefillingTest')
    for row in table:
        i+=1
        for row1 in table1:
            if row1[0]==row[0]:
                PInf=PurV(row1[1],row1[4])
                RInf=RefV(row1[10])
        Pur.append(PInf)
        Ref.append(RInf)
    n=i-1
    return render_template(
        'rwhub.html',
        year=str(datetime.now().day)+'/'+str(datetime.now().month)+'/'+str(datetime.now().year),name=name,table=table,numb=n,Pur=Pur,Ref=Ref
    )

@app.route('/database')
def database():
    """Renders the database page for the Admin."""
    global numb, datat
    numb=5
    datat=[]
    data1=opendatabase('GenTest.sqlite','SELECT * FROM GenRefillingTest')
    for  i in range(len(data1)):
        datat.append(data1[len(data1)-i-1])
    with open('Fueling.csv', 'w', newline="") as f:
        writer = csv.writer(f,delimiter=';')
        writer.writerow(['Site', 'Purchase_Quantity', 'Purchase_Date','Purchase_Time','Payment','Station','Seller_Name','Volume','Refilling_Date','Refilling_Time','Verify'])
        writer.writerows(datat)
    shutil.move("Fueling.csv", "E:\DSP\DSP\DSP\static\Output\Fueling.csv")
    data2=datat[:numb]
    return render_template(
        'database.html',
        year=str(datetime.now().day)+'/'+str(datetime.now().month)+'/'+str(datetime.now().year),
        data=data2, name=name
    )


@app.route('/tableview')
def tableview():
    global datat
    global numb
    data1=opendatabase('GenTest.sqlite','SELECT * FROM GenRefillingTest')
    for  i in range(len(data1)):
        datat.append(data1[len(data1)-i-1])
    if numb<len(data1):
        numb+=1
    data2=datat[:numb]
    return render_template( 'database.html',
        title='database',
        year=str(datetime.now().day)+'/'+str(datetime.now().month)+'/'+str(datetime.now().year),
        data=data2, name=name, num=numb+1)


@app.route('/sitegraph/')
def sitegraph(): # function produces monthly picture on the siteprofile page
    global name
    graph = pygal.Bar()
    data=opendatabase('GenTest.sqlite','SELECT * FROM GenRefillingTest')
    graph.title = 'Comparism of different sites refueling monthly '
    dataj=['Start']
    month=str(datetime.now().month)+'/'+str(datetime.now().year)
    for row in data:
        fdate=str(row[8][5:7])+'/'+str(row[8][:4])
        if fdate==month: 
            dataj.append(row[0])  
            graph.add(row[0],  row[7])
    graph_data = graph.render_data_uri()
    return render_template("siteprofile.html", graph_data = graph_data,name=name,year=str(datetime.now().day)+'/'+str(datetime.now().month)+'/'+str(datetime.now().year),title='Sitegraph')


@app.route('/sitegraph1', methods=['get','post'])
def sitegraph1(): # function that causes the change of graph on the siteprofile page
    global name
    graph = pygal.Bar()
    data=opendatabase('GenTest.sqlite','SELECT * FROM GenRefillingTest')
    graph.title = 'Comparism of different sites refueling monthly '
    dataj=['Start']
    month=str(request.values.get('smonth'))+'/'+str(request.values.get('syear'))
    for row in data:
        fdate=str(int(row[8][5:7]))+'/'+str(row[8][:4])
        if fdate==month: 
            dataj.append(row[0])  
            graph.add(row[0],  row[7])
    graph_data = graph.render_data_uri()
    return render_template("siteprofile.html", graph_data = graph_data,name=name,year=str(datetime.now().day)+'/'+str(datetime.now().month)+'/'+str(datetime.now().year),title='Sitegraph')


@app.route('/purchase_order',methods=['get', 'post'])
def purchase_order(): # compares the values input to that in the database
    """Renders the about page."""
    global site
    Site=request.values.get('Site')
    Quan=request.values.get('Quan')
    Date=str(date.today()).split()[0] 
    Time=strftime("%H:%M:%S")
    conn = sqlite3.connect('Register.sqlite') # Open database
    cursor = conn.cursor()
    query="INSERT INTO Purchase_Order (Site,Quantity,Date,Time) VALUES (?,?,?,?)"
    cursor.execute(query,(Site,Quan,Date,Time))
    conn.commit()
    #SendSMS()
    sendmail("ebude.yolande@aims-cameroon.org",'DMS | RefuelingWeb - Purchase Order','Greetings,' +'\n'+'\n'+'Fuel to be purchase for '+Site+'\n'+'Volume: '+Quan+ ' l'+'\n'+'\n'+'\n'+'kind regards'+'\n'+'RefuelingWeb Team')
    #sendmail("gabriel.dima@firstgroup.immo",'DMS | RefuelingWeb - Purchase Order','Greetings,' +'\n'+'\n'+'Fuel to be purchase for '+Site+'\n'+'Volume: '+Quan+ ' l'+'\n'+'\n'+'\n'+'kind regards'+'\n'+'RefuelingWeb Team')
    #sendmail("patrick.dima@manpowercam.com",'DMS | RefuelingWeb - Purchase Order','Greetings,' +'\n'+'\n'+'Fuel to be purchase for '+Site+'\n'+'Volume: '+Quan+ ' l'+'\n'+'\n'+'\n'+'kind regards'+'\n'+'RefuelingWeb Team')
    #sendmail("jocelyn.zacko@aims-cameroon.org",'DMS | RefuelingWeb - Purchase Order','Greetings,' +'\n'+'\n'+'Fuel to be purchase for '+Site+'\n'+'Volume: '+Quan+ ' l'+'\n'+'\n'+'\n'+'kind regards'+'\n'+'RefuelingWeb Team')
    return render_template(
        'rwss.html',
        year=str(datetime.now().day)+'/'+str(datetime.now().month)+'/'+str(datetime.now().year))


####### Output from Database to be used#####
#####



def PurV(a,b): #Verify if ammount paid for purchase 
    if float(a)*600==float(b):
        return  "Purchase Amount Accepted!!!" 
    else:
        return  "Purchase Amount Denied!!!" 
    
def RefV(a): #Verify if refilling was ok
    if a=='1':
        return  "Fueling Welldone!!!" 
    if a=='0':
        return "Attention theft!!!" 

def CurrentINFO(row): #Give out information on fueling.
    CurIN=[]
    PInf=''
    RInf=''
    PInf=PurV(row[1],row[4])
    CurIN=[row[0],row[5],row[6],row[7],row[4],row[1]]
    RInf=RefV(row[10])     
    return  CurIN,PInf,RInf,row[8],row[9]        

def PreviousINFO(row1): #Give out information on fueling

    #Initialization of Local variable
    CurIN=[]
    PInf=''
    RInf=''
    Arr=[]
    #Searching for Info in table
    i,j,k=0,0,0
    data = opendatabase('GenTest.sqlite','SELECT * FROM GenRefillingTest')
    for row in data:
        if row[0]==row1[0]:# searching for generator
            Arr.append(row)
    for row in Arr: 
       if row[0]==row1[0] and row[9]==row1[9] and j>0:
           row=Arr[j-1]
           PInf=PurV(row[1],row[4])
           CurIN=[row[0],row[5],row[6],row[7],row[4]]
           RInf=RefV(row[10]) 
           return  CurIN,PInf,RInf,row[8],row[9]
       else:
           PInf=''
           CurIN=[]
           RInf=''
       j+=1
    return  CurIN,PInf,RInf,row[8],row[9]    

def IntervalINFO(row): #Time interval of refueling a generator
    a,b,c,date1,time1=PreviousINFO(row)
    d,e,f,date2,time2=CurrentINFO(row)
    D1=date1.split('-')
    D2=date2.split('-')
    Date1=date(int(D1[0]),int(D1[1]),int(D1[2]))
    Date2=date(int(D2[0]),int(D2[1]),int(D2[2]))
    Days=(Date2-Date1).days
    Time1=strptime(time1,'%H:%M:%S')
    Time2=strptime(time2,'%H:%M:%S')
    if Time2[3]>Time1[3]:
        Hours=Time2[3]-Time1[3]
    else:
        Hours=Time1[3]-Time2[3]
    return Days,Hours
    
def fillVisual():
    conn = sqlite3.connect('Visual.sqlite')
    cursor = conn.cursor()
    cursor.execute("DELETE FROM TVisual")
    p1=0
    data=opendatabase('GenTest.sqlite','SELECT * FROM GenRefillingTest')
    for row in data:
        a,b,c,d,e=CurrentINFO(row)
        f,g,h,i,j=PreviousINFO(row)
        day,hour=IntervalINFO(row)
        if a[5]-a[3]<0:
            genc='Volume in tank: '+ str(a[3])+' l, '+'Payment:'+ str(a[4])+' FCFA, '+'Station: '+str(a[1])+', '+'Volume difference: 0.0 l not placed in the tank'
        else:
            genc='Volume in tank: '+ str(a[3])+' l, '+'Payment:'+ str(a[4])+' FCFA, '+'Station: '+str(a[1])+', '+'Volume difference: '+ str(a[5]-a[3])+' l not placed in the tank'
        if f==[]:
            genf= "No previous refilling"
            geni= "First Refiling"
        else:
            genf='Volume in tank: '+ str(f[3])+' l, '+'Payment:'+ str(f[4])+' FCFA'
            geni=str(day)+' Days '+'and '+str(hour)+' hours'
            query = "delete from TVisual where Generator = '%s' " % row[0]
            cursor.execute(query)
        query="INSERT INTO TVisual (Generator,Current_Refilling,Previous_Refilling,Interval) VALUES (?,?,?,?)"
        cursor.execute(query,(row[0],genc,genf,geni))
        p1+=1
        conn.commit()

    return p1
    



###############Comparative study ###########################
############################################################

def VolCompare(Prow,Frow): #Compare Volume of different generators
    if Frow[0]==Prow[0]: #comparing the Generator names
        if Frow[1]==Prow[3]: #comparing the volume bought, refilled and fueled into the generator. 
            F='1'
        else:
            if (float(Prow[3])-float(Frow[1]))/float(Frow[1]) < 2/float(Frow[1]): #Accept slight loss of volume
                F='1'
            else:
                F='0'
    else:
        F='0'
    return  F

def Organiser(i,k): #Searches and matches the right information
    p=k-i-5
    Purextra=[]
    Fuextra=[]
    Refextra=[]
    List1=[]
    FinalL=[]
    while(p<k):#Keep the new data in a list
        dataP = opendatabase("GenRefillingDatabase.sqlite",'SELECT * FROM GenPurchaseData')
        Purextra.append(dataP[p]) #Fetch all new info on purchase
        p=p+1
    #print(Purextra)
    dataF = opendatabase("GenRefillingDatabase.sqlite",'SELECT * FROM GenFuelingData') # fetch new data collected from generator
    for t in range(len(dataF)):
        for l in range(len(Purextra)):
            if dataF[t][0]==Purextra[l][0]:
                    List1.append(Purextra[l]+dataF[t] )#make a list of Purchase and Fueling of generators
                   
    for r in range(len(List1)):
        FinalL=List1[r]#make a list of one generators whose refilling information has arrive.
    # Converting all int and floats to string
    for h in range(6): 
        Prow[h]=str(FinalL[h])
    for h in range(4):
        Frow[h]=str(FinalL[h+7])
    #print(FinalL)
    F=VolCompare(Prow,Frow) #Verify if the fueling process has been carried out without fault.
    return F,Prow,Frow
    




F=''
i,k,h=0,0,0
    
# Open the two database and read their tables


data1 = opendatabase("GenRefillingDatabase.sqlite",'SELECT * FROM GenFuelingData')
for Frow in data1:
    i=i+1
Frow=np.array(Frow)
    
data1 = opendatabase("GenRefillingDatabase.sqlite",'SELECT * FROM GenPurchaseData')
for Prow in data1:
    k=k+1
Prow=np.array(Prow)


data1 = opendatabase("GenTest.sqlite",'SELECT * FROM GenRefillingTest')
for Trow in data1:
    h+=1
Trow=np.array(Trow)




#Searching for new info and place in the Database
F,Prow,Frow=Organiser(i,k)
if Frow[0]==Trow[0] and Frow[1]==Trow[7] and Frow[2]==Trow[8]: #ensure no repitition in the main database
    print('No new fueling Information')
else:
    conn = sqlite3.connect('GenTest.sqlite') # Open database
    c = conn.cursor()
    c.execute("INSERT INTO GenRefillingTest (Site, Purchase_Quantity, Purchase_Date, Purchase_Time, Payment, Station, Seller_Name, Volume, Refilling_Date, Refilling_Time, Verify) VALUES (?, ?, ?, ?, ?,?,?,?,?,?,?)",(Prow[0],Prow[3],Prow[4],Prow[5],Prow[6],Prow[1],Prow[2],Frow[1],Frow[2],Frow[3],F))
    conn.commit()
    print('New fueling information')

#############################################  RefuelingWeb  ######################################################## 



#############################################  Anomaly Detection  ####################################################

cur_dir = os.path.dirname(__file__)
path = 'E:\DSP\DSP\DSP'
clf = pickle.load(open(os.path.join(cur_dir, 'pkl_objects\svm.pkl'), 'rb'))
UPLOAD_FOLDER = "E:\DSP\DSP\DSP"

@app.route('/adhome')
def adhome():
    global name
    """Renders the first page."""
    return render_template(
        'adfirst.html',
        year=datetime.now().year, name=name
    )


def gettable():
	List=[]
	for i in range(1,36):
		if i==1 or i==8 or i==15 or i==22 or i==29:
			List.append(request.form[str(i)])
		else:
			if request.form[str(i)]=='':
				List.append(0.0)
			else:
				List.append(float(request.form[str(i)]))

	s = pd.DataFrame([List[:7],List[7:14],List[14:21],List[21:28],List[28:35]])
	s.columns= [ 'Site Name', 'CONSUMPTION_RATE', 
                         'RUNNING_TIME', 'NUMBER_OF_DAYS', 'CONSUMPTION_HIS', 
                         'PREVIOUS_FUEL_QTE', 'QTE_FUEL_FOUND']
	return s


@app.route('/predicttable',methods = ['POST','GET'])
def predicttable():
	Data = gettable()
	Data['consumption_perDay_within_a_period'] = Data['CONSUMPTION_HIS']/(Data['NUMBER_OF_DAYS'])
	Data.loc[~np.isfinite(Data['consumption_perDay_within_a_period']), 'consumption_perDay_within_a_period'] = 0
	Data['Quanitity_consumed_btn_visits'] = Data['PREVIOUS_FUEL_QTE'] - Data['QTE_FUEL_FOUND']
	Data['Quanitity_consumed_btn_visits_Per_Day'] = Data['Quanitity_consumed_btn_visits']/(Data['NUMBER_OF_DAYS'])
	Data.loc[~np.isfinite(Data['Quanitity_consumed_btn_visits_Per_Day']), 'Quanitity_consumed_btn_visits_Per_Day']= 0
	Data['Running time per day'] = Data["RUNNING_TIME"]/Data["NUMBER_OF_DAYS"]             
	Data.loc[~np.isfinite(Data['Running time per day']), 'Running time per day'] = 0
	Data['Maximum_consumption_perDay'] = Data[['CONSUMPTION_RATE']]*24
	X = Data [['CONSUMPTION_RATE','Running time per day','consumption_perDay_within_a_period','Maximum_consumption_perDay']]
	resfinal = clf.predict(X)
	l=X.index.values
	label = {0: 'Anomaly', 1: 'Normal Consunption'}
	Site=Data['Site Name'][l].values
	pred=list(resfinal)
	RF_Predict_Data = pd.DataFrame({'Site Name': Site,
	'Predictions': pred})
	for k in range(RF_Predict_Data.shape[0]):
	    if RF_Predict_Data ['Predictions'][k]==0:
	        RF_Predict_Data ['Predictions'][k] = 'Anomaly'
	    else:
	        RF_Predict_Data ['Predictions'][k]= 'normal'
	RES1 = RF_Predict_Data[RF_Predict_Data['Predictions']=='Anomaly']
	RES2 = RF_Predict_Data[RF_Predict_Data['Predictions']=='normal']
	
	return  render_template(
        'adrt.html',
        year=datetime.now().year, name=name, RA=RES1, RN=RES2
    )

def uploader():
    if request.method == 'POST':
        f = request.files['file']
        absolute_file = os.path.abspath(UPLOAD_FOLDER + f.filename)		
        f.save(absolute_file)
    return absolute_file

@app.route('/loadingpre',methods = ['GET', 'POST'])
def loadingpre():
    global RES1,RES2
    path=uploader()
    Data=pd.read_excel(path)
    col = Data.columns
    Data = Data
    Data['consumption_perDay_within_a_period'] = Data['CONSUMPTION_HIS']/(Data['NUMBER_OF_DAYS'])
    Data.loc[~np.isfinite(Data['consumption_perDay_within_a_period']), 'consumption_perDay_within_a_period'] = 0
    Data['Quanitity_consumed_btn_visits'] = Data['PREVIOUS_FUEL_QTE'] - Data['QTE_FUEL_FOUND']
    Data['Quanitity_consumed_btn_visits_Per_Day'] = Data['Quanitity_consumed_btn_visits']/(Data['NUMBER_OF_DAYS'])
    Data.loc[~np.isfinite(Data['Quanitity_consumed_btn_visits_Per_Day']), 'Quanitity_consumed_btn_visits_Per_Day']= 0
    Data['Running time per day'] = Data["RUNNING_TIME"]/Data["NUMBER_OF_DAYS"]             
    Data.loc[~np.isfinite(Data['Running time per day']), 'Running time per day'] = 0
    Data['Maximum_consumption_perDay'] = Data[['CONSUMPTION_RATE']]*24
    X = Data [['CONSUMPTION_RATE','Running time per day','consumption_perDay_within_a_period','Maximum_consumption_perDay']]
    resfinal = clf.predict(X)
    l=X.index.values
    label = {0: 'Anomaly', 1: 'Normal Consunption'}
    Site=Data['SITE_NAME'][l].values

    pred=list(resfinal)

    RF_Predict_Data = pd.DataFrame({'Site Name': Site,
	'Predictions': pred})
    for k in range(RF_Predict_Data.shape[0]):
        if RF_Predict_Data ['Predictions'][k]==0:
            RF_Predict_Data ['Predictions'][k] = 'Anomaly'
        else:
            RF_Predict_Data ['Predictions'][k]= 'normal'

    RES1 = RF_Predict_Data[RF_Predict_Data['Predictions']=='Anomaly']
    RES2 = RF_Predict_Data[RF_Predict_Data['Predictions']=='normal']

    return render_template(
        'adrtu.html',
        year=datetime.now().year, name=name, RA=RES1
    )


@app.route('/adsitegraph')
def adsitegraph():
    global RES1,RES2
    pp = []
    pp.append(RES1['Predictions'].count())
    pp.append( RES2['Predictions'].count())
    graph = pygal.Bar()
    graph.title = 'Graphical Representation'
    graph.add('Anormaly',pp[0])
    graph.add('Normal',pp[1])
    graph_data = graph.render_data_uri()
    return render_template("graphdisplay.html", graph_data=graph_data)

#############################################  Anomaly Detection  ####################################################




#######################################  Fuel Consumption Prediction  ################################################

cur_dir = os.path.dirname(__file__)
clf = pickle.load(open(os.path.join(cur_dir,
			'pkl_objects\Best_GB_Fuel_Model.pkl'), 'rb'))

@app.route('/fcphome')
def fcphome():
    global name
    """Renders the login page."""
    return render_template(
        'fcpfirst.html',
        year=datetime.now().year, name=name
    )


def results():
    global RF_Predict_Data
    path=uploader()
    Clusters=pd.read_excel(path)
    Clusters['Fuel_per_period']=Clusters['PRE_QTE_FUEL']-Clusters['QTE_FUEL_FOUND']
    Data=Clusters[['Fuel_per_period','RUNNING_TIME','CONSUMPTION_RATE','NUMBER_OF_DAYS']]
    resfinal = clf.predict(Data)
    l=Data.index.values
    clus=Clusters['CLUSTER'][l].values
    site=Clusters['SITE_NAME'][l].values
    pred=list(resfinal)
    RF_Predict_Data = pd.DataFrame({'Clusters': clus,
	'Site Name':site,
	'Predictions': pred})
    return  RF_Predict_Data

@app.route('/fcpresult',methods = ['GET', 'POST'])
def fcpresult():
    global resu
    resu=results()
    return render_template(
        'fcprs.html',
        year=datetime.now().year, name=name, RA=resu)

@app.route('/clustergraph',methods = ['GET', 'POST'])
def clustergraph():
    global resu
    resu=resu.groupby(['Clusters']).sum()
    graph = pygal.Bar()
    graph.title = 'Prediction of Fuel Consumption Per Cluster'
    for k in resu.index:
    	graph.add(k,resu['Predictions'][k])
    graph_data = graph.render_data_uri()
    return render_template("graphdisplay.html", graph_data=graph_data)



#######################################  Fuel Consumption Prediction  ################################################

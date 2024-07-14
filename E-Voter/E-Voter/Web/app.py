import os
import shutil
from flask import Flask, render_template, request, Response, send_file, redirect, url_for, jsonify, request, render_template
from camera import Camera
from fileinput import filename
import cv2
from datetime import datetime
import matplotlib.pyplot as plt
from flask import session
from dbconnect import *
from blockchain import blockchain
from fileinput import filename
import rsa
from flask import session
import pickle

app = Flask(__name__)
app.config['SESSION_TYPE'] = 'memcached'
app.config['SECRET_KEY'] = 'super secret key'
app.config["UPLOAD_FOLDER"] = "static/NomineesImages/"
camera = None
voterInformationDic = []
detection_model_path = 'haarcascade_frontalface_default.xml'

def get_camera():
    global camera
    if not camera:
        camera = Camera()

    return camera


@app.route('/')
def root():
    
    return redirect(url_for('index'))

def smartContract():
         smart = []
         query = 'select * from blockchain'
         result=recoredselect(query)
         for xx in result:
              voterInfo =xx[3]
              vv = voterInfo.split(",")
              scontract = {'voterid':vv[0],'eid':vv[1],'nid':vv[2]}
              smart.append(scontract)
              filename = 'evotingInfo.sav'
              pickle.dump(smart, open(filename, 'wb'))
              return smart
def userAlreadyVotedForThisElection():
       smartValues =   smartContract()
       for dictionary in smartValues:
            for key, value in dictionary.items():
                print(f"{key}: {value}")
            print("---")
def getLastElectionId():
     query ='select *from election ORDER BY id DESC LIMIT 1'
     result=recoredselect(query)
     return result[0][1]

def countVote(currentEID):
     query ='SELECT nomineeid, COUNT(*) AS vote FROM `electionconduct` where electionId ="%s" GROUP BY nomineeid'   % \
                (currentEID)
     result=recoredselect(query)
     tt = []
     for x in result:
         ss = {x[0]:x[1]}
         tt.append(ss)
     return tt


     

@app.route('/index/')
def index():
    status ='assigned'
    electionDateResult = electionDateEvaluation(status)
    
    if(electionDateResult):
        print('value printed')
        statusChange()
    currentEId= getLastElectionId()
    totalVote =countVote(currentEId)
    
    voterInformationDic= smartContract()
    sql='SELECT electionconduct.electionId,electionconduct.nomineeid,nominees.username,nominees.email,nominees.team,nominees.imgpath, count(*) as voteCount FROM `electionconduct` JOIN nominees on electionconduct.nomineeid = nominees.id where electionconduct.electionId="%s" group by nomineeid'% \
                (currentEId) 
    result=recoredselect(sql)
    
   
                   
    return render_template('index.html', data = result )



def gen(camera):
    while True:
        frame = camera.get_feed()
        if frame:
            yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
        else:
            raise RuntimeError("No frame captured.")

@app.route('/video_feed/')
def video_feed():
    camera = get_camera()
    return Response(gen(camera),
        mimetype='multipart/x-mixed-replace; boundary=frame')

import face_recognition
import pickle
from sklearn.ensemble import RandomForestClassifier


@app.route('/capture/<userid>')
def capture(userid):
    camera = get_camera()
    stamp = camera.capture()
    imgFile = 'captures/' + stamp +".jpg"
    image_path = "static/"+imgFile
    print(image_path)
    known_image = face_recognition.load_image_file(image_path)
    encoding = face_recognition.face_encodings(known_image)[0]
    testValue = [encoding]
    file = open('voterModel.sav', 'rb')
    encodedDatas = pickle.load(file)
    y_pred = encodedDatas.predict(testValue)
    if(userid ==y_pred ):
         
         return redirect("/votingurl")
         
    else:
         return render_template('faceCollection.html',data = "Sorry Facial Feature mismatched")
    
@app.route('/votingurl',methods = ["GET","POST"])
def votingurl():
         status = 'assigned'
         electionsql='select * from  election where status="%s"'   % \
                                    (status)
         electionresult=recoredselect(electionsql)
         electionId =  electionresult[0][1]
         electionName  = electionresult[0][2]
         nomineessql='select * from  nominees'   
         nomineesresult=recoredselect(nomineessql)
         return render_template('addmyVotes.html',electionId = electionId,electionName = electionName,nomineesInfo =nomineesresult)

@app.route('/SaveVoter',methods = ["GET","POST"])
def SaveVoter():
        uname = request.form["username"]
        email = request.form["email"]
        contact = request.form["contact"]
        uniqueid = request.form["uniqueid"]
        password = request.form["password"]
        sql1='insert into votes(name, email,contact,voterid,password) values("%s","%s","%s","%s","%s")' % \
                (uname,email,contact,uniqueid,password)
        print(sql1)
        inserquery(sql1)
        message="Added Sucessfully"
        bsql='select * from  votes'   
        bresult=recoredselect(bsql)
        return render_template('addVoters.html',mess=message, eview= bresult)


def checkElectionAssigned():
      sta ='assigned'
      sql1='select * from election where status ="%s"' % \
                    (sta)
      print(sql1)
      res  = recoredselect(sql1)
      return len(res)

@app.route('/SaveElections',methods = ["GET","POST"])
def SaveElections():
        eid = request.form["eid"]
        ename = request.form["ename"]
        edate = request.form["electionDate"]
        status ='assigned'
        ell = checkElectionAssigned()
        esql='select * from  election'   
        eresult=recoredselect(esql)
        print('Check:'+eresult[0][0])
        if(ell>0):
             
             return render_template('addElections.html',mess='There is already election was assigned which need to be complete', eview = eresult) 
        else:
            sql1='insert into election(eid, ename,edate,status) values("%s","%s","%s","%s")' % \
                    (eid,ename,edate,status)
            print(sql1)
            inserquery(sql1)
            message="Added Sucessfully"
            return render_template('addElections.html',mess=message, eview = eresult)







@app.route('/loginverification',methods = ["GET","POST"])
def loginverification():
        
        uname = request.form["username"]
        email = request.form["email"]
        contact = request.form["contact"]
        team = request.form["team"]
       
        f = request.files['imgpath']
        f.save(app.config['UPLOAD_FOLDER'] +f.filename)  
        bsql='select * from  nominees'   
        bresult=recoredselect(bsql)
        print(f.filename) 
        sql1='insert into nominees(username, email,contact,team,imgpath) values("%s","%s","%s","%s","%s")' % \
                (uname,email,contact,team,f.filename)
        print(sql1)
        inserquery(sql1)
        message="Added Sucessfully"
        return render_template('addCandidates.html',mess=message, eview = bresult)

@app.route('/viewallNominees')
def viewallNominees():

        sql='select * from  nominees ' 
        result=recoredselect(sql)
        return render_template('./index.html',data=result)

@app.route('/loginPage')
def loginPage():
    return render_template('login.html')

@app.route('/addCandidates')
def addCandidates():
    bsql='select * from  nominees'   
    bresult=recoredselect(bsql)
    return render_template('addCandidates.html', eview= bresult)

@app.route('/blockchainVotes')
def blockchainVotes():
    bsql='select * from  blockchain'   
    bresult=recoredselect(bsql)
    return render_template('blockchain.html', eview= bresult)


@app.route('/addVoters')
def addVoters():
    bsql='select * from  votes'   
    bresult=recoredselect(bsql)
    return render_template('addVoters.html', eview= bresult)

@app.route('/addElections')
def addElections():
    esql='select * from  election'   
    eresult=recoredselect(esql)
    
    return render_template('addElections.html', eview = eresult)

@app.route('/addmyVotes')
def addmyVotes():
    status = 'assigned'
    sql1='select * from  election where status="%s"'   % \
                        (status)
    eresult=recoredselect(sql1)
    print(eresult)

    return render_template('addmyVotes.html')

@app.route('/authentication',methods = ["GET","POST"])
def authentication():
        email = request.form["email"]
        password = request.form["password"]
        if(email == 'admin@gmail.com' and password=='admin'):
            session['usertype']="Admin"
            session['name']="Admin"
            nn =  session['name']
            return render_template('admin.html',mess=nn)            
        else:
            sql='select * from  votes where email="%s" and password="%s"'   % \
             (email,password)
            result=recoredselect(sql)
            print(result)
            if(len(result)==0 ):
                        return render_template('login.html',mess="User Not Exist")
            else:                  
                    session['id'] = result[0][0]
                    session['aadharid'] = result[0][4]
                    session['name'] = result[0][1]
                    status = 'assigned'
                    electionsql='select * from  election where status="%s"'   % \
                                    (status)
                    electionresult=recoredselect(electionsql)
                    if(len(electionresult)>0):
                         edate = electionresult[0][3]+' '
                         eid = electionresult[0][1]
                         datetime_object = datetime.strptime(edate , '%m/%d/%y ')
                         tt = (datetime.now() -datetime_object).days
                         print('daydiff:'+str(tt))
                         if(tt==0):
                                smartValues =   smartContract()
                                if(smartValues==None):
                                     return render_template('faceCollection.html')
                                else:
                                  for dictionary in smartValues:
                                            vid = dictionary["voterid"]
                                            electionId = dictionary["eid"]
                                            if(vid==session['aadharid'] and eid==electionId):
                                                return render_template('login.html', mess='Already Voted for this election')
                                            else:
                                                return render_template('faceCollection.html')   
                                     
                                
                                                
                                         
                                
                         else:
                                mess = "Sorry there is no election assigned today"
                                return render_template('login.html', mess=mess)
                            
                    else:
                         mess = "Sorry there is no election assigned"
                         return render_template('login.html', mess=mess)



def electionDateEvaluation(status):
     electionsql='select * from  election where status="%s"'   % \
                                    (status)
     tt = False
     electionresult=recoredselect(electionsql)
     if(len(electionresult)>0): 
              edate = electionresult[0][3]+' '
              datetime_object = datetime.strptime(edate , '%m/%d/%y ')
              diff = (datetime.now()-datetime_object).days
              if(diff<0):
                   return True
              elif(diff==0):
                   return False
              else:
                   return True
                   
              

def statusChange():
    status1 = 'assigned'
    status2 = 'completed'
    sql = 'UPDATE election SET status = "completed" where status ="assigned"'
    updatequery(sql)
    

@app.route('/addVotes',methods = ["GET","POST"])
def addVotes():
    voterId = request.form["userId"]
    electionId = request.form["electionId"]
    nomineeId = request.form["nomineeId"]
    myBlocks = blockchain(voterId,electionId,nomineeId)
    result = myBlocks.addBlocks()
    print(result)
    mess =''
    bsql='select * from  blockchain'   
    bresult=recoredselect(bsql)
    
    if(result):
         mess ="Already Voted to this election"
    else:
         electionConduct='insert into electionconduct (electionId,nomineeid,voterid,cdate)values("%s","%s","%s","%s")' % \
                                    (electionId,nomineeId,voterId,datetime.now())
         inserquery(electionConduct)
         mess="successfully voted"
    return render_template('addmyVotes.html',data=mess, eview = bresult)               

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8080, debug=True)

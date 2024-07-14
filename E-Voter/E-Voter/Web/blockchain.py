
from time import localtime, strftime
from dbconnect import *
import random
import hashlib
from datetime import datetime
class blockchain():
    
    def __init__(self, voterId, electionId,nomineeId):
            self.nomineeId = nomineeId
            self.electionId = electionId
            self.voterId = voterId
        

    def checkUserAlreadyVote(self):
        
        userInfo="select * from  electionconduct where electionId='"+self.electionId+"'  and voterid='"+self.voterId+"'" 
        result = recoredselect(userInfo)
        isExist = False
        if(len(result)>0):
              isExist =True
        return isExist
    
    def genesisBlock(self):
        blockInfo='select * from  electionconduct'   
        result = recoredselect(blockInfo)
        isExist = False
        if(len(result)==0):
             isExist =True
        return isExist

    def findPreviousHashValue(self):
        query = 'select * from blockchain ORDER BY id DESC LIMIT 1' 
        result = recoredselect(query)  
        cHash = result[0][2]
        return cHash 
    
    
    def addBlocks(self):
         alreadyVoted = False
         userAlreadyExist = self.checkUserAlreadyVote()
         if(userAlreadyExist):
              alreadyVoted = True
         else:
            isGensis = self.genesisBlock()
            randomGenerate = random.randint(0,9)
            pHash =''
            transaction = self.voterId+','+self.electionId+','+self.nomineeId
            timeStamp = strftime("%d-%m-%Y-%Hh%Mm%Ss", localtime())
            hasingProcess = hashlib.sha512(str(randomGenerate).encode())
            cHash = hasingProcess.hexdigest()
            if(isGensis):
                pHash='00000'
            else: 
                pHash = self.findPreviousHashValue()
            sql1='insert into blockchain(previoushash,currenthash,transaction,timeinfo) values("%s","%s","%s","%s")' % \
                                    (pHash,cHash,transaction,timeStamp)
            inserquery(sql1)
            
            return alreadyVoted
     
              
  
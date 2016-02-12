#this script was created to parse firebase to retrieve input
#information to run the youcoin.py program
#It is not finished, but it is here to scaffold the 
#finalization of the parser

#Check https://pypi.python.org/pypi/python-firebase/1.2 to get api
from firebase import firebase
import json

#the name of your requested firebase url
fbDomain = 


firebase = firebase.FirebaseApplication(fbDomain, None)
result = firebase.get('/', None)

#print(result.get("apikey"))

for key in result:
   code = result[key]
   codeList = code.split(";")
   record1 = codeList[0]
   score = int(codeList[1]) + 3
   firebase.delete("/" + key,0)

   
   endR = record1 + ";" + str(score)
   firebase.post('/',endR)


#print(codeList[])


#result1 = firebase.post('/', new_user)


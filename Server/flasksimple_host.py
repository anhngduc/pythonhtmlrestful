from flask import *
import mysql.connector


app = Flask(__name__)
 
@app.route('/pjson', methods = ['POST'])
def postJsonHandler():  
  print (request.json)  
  #content = request.get_json()
  #print ('Got this: '+content)  
  
  data = json.loads(request.json)
  messageid = data['mid']
  rackid= data['rackid']
  packid= data['packid']
  #packid= request.json.get('packid', '')	
  #time = request.json.get('time', '')
  print ("")
  print('Request ID: '+str(messageid) +' detail ----- Package ' + packid + ' at ' + rackid)
  #print('Time = ' +time )
  return 'done'
 
app.run(host='0.0.0.0', port= 5000)
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
  warehouseid = data['warehouseid']
  #packid= request.json.get('packid', '')	
  #time = request.json.get('time', '')
  print ("")
  print('Request ID: '+str(messageid) +' detail ----- Package ' + packid + ' at ' + rackid)
  cnx = mysql.connector.connect(user="root",password="213", database='warehouse')
  cursor = cnx.cursor()
  #update package location
  querry="""
          SELECT palletid FROM pallets WHERE palletid =%S
          """,(packid)
  cursor.execute(querry)
  rows = cursor.fetchall()
  if len(rows) >0:
    querry = """
              update pallets set  location =%s where palletid= %s;
              """,(rackid,packid)
  else:
    querry="""
            INSERT INTO pallets (palletid,location,material,color,onwer,length,width) VALUES (%s,%s,'Plastic','Red','EnW',110,110);
            """,(packid,rackid)
  cursor.execute(querry)
  rows = cursor.fetchall()
  
  #update rackid to warehouse
  querry="""
          SELECT rackid FROM rackids WHERE rackid =%s
          """,(rackid)
  cursor.execute(querry)
  rows = cursor.fetchall()
  if len(rows) >0:
    querry = """
              update rackids set  warehouse =%s where rackid= %s;
              """,(warehouseid,rackid)
  else:
    querry="""
            INSERT INTO rackids (rackid,warehouse,type,row,rcolumn,level) VALUES ('%s','%s','R',1,1,1);
            """,(warehouseid,rackid)
  cursor.execute(querry)
  rows = cursor.fetchall()
  
  return 'done'
 
app.run(host='0.0.0.0', port= 5000)
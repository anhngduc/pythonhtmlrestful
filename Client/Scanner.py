# This Python file uses the following encoding: utf-8
import os, sys
import requests
import json
import mysql.connector
from Tkinter import *
import math
import threading
from multiprocessing import cpu_count
import time
import Queue
import tkMessageBox
from platform import system as system_name # Returns the system/OS name
from os import system as system_call       # Execute a shell command
import logging
import ttk
#from ttk import Treeview
exitFlag = 0
hostname = "192.168.1.134"
url = 'http://'+ hostname+':5000/pjson'    

class sendmessage(threading.Thread):
    def __init__(self,name,threadID,q):
        threading.Thread.__init__(self)
        self._threadID= threadID
        self._name=name
        self._send_queue=q
        
    def run(self):
        print "Start thread: " + self._name
        process_data(self._name,self._send_queue)
        print "exit thread" + self._name
    
def process_data(threadName,q):
    global exitFlag
    global my_gui
    print 'call from: ' + threadName
    x=0
    while True:
        #print "Count " + str(x)
        #x=x+1
        if send_queue.empty():
            print "send_queue is empty"
        print "Exit flag = " + str(exitFlag)
        if exitFlag == 1 and send_queue.empty():
            print "exit now"
            return
        queuelock.acquire() 
        r=0
        if not send_queue.empty():
            if exitFlag == 1:
                print "Please go to wifi zone"
                #tkMessageBox.showinfo("Warning!!", "Go to WIFI zone to synchronize FIRST, force stop result in LOST data!!")
            data=send_queue.get()
            queuelock.release()
            print 'sending data %s - %s' % (data[0],data[1])
            result= False
            my_gui.treeview.item(data[2], tags=('working'))
              
            try:
                result=send_data(x,data[0],data[1])
            except:
                print "Error",sys.exc_info()[0]
            if not result:
                print "sending fail"
                my_gui.treeview.item(data[2], tags=('newitem'))
                datapack=(data[0],data[1],data[2])
                queuelock.acquire()        
                send_queue.put(datapack)
                queuelock.release()
            else:
                my_gui.treeview.item(data[2], tags=('success'))
                r=r+1
        else:    
            queuelock.release()
            time.sleep(1)
    return            
queuelock=threading.Lock()
send_queue = Queue.Queue(1000)
class userUI:
    
    
    def __init__(self,master,username,userlocation):
        self.master=master
        master.title("Location import")                 
        self._idcounter=0
        self.L1= Label(self.master,text="Rack ID:").grid(sticky=W,padx=5, pady=5)        
        self.E1= Entry(self.master,width=20)
        self.E1.grid(row=0,column=1,sticky=W,padx=5, pady=5)
        
        self.L2= Label(self.master,text="Pack ID:").grid(row=0,column=2,sticky=W,padx=5, pady=5)
        
        self.E2= Entry(self.master,width=20)
        self.E2.grid(row=0,column=3,sticky=W,padx=5, pady=5)
        
        #self.btn1=Button(self.leftFrame,text="Upload",command=self.send_data(self.E1.get(),self.E2.get()))
        self.btn1=Button(self.master,text="Upload",command=self.hello).grid(row=0,column=4,sticky=W,padx=5, pady=5)

        self.framex=Frame(master)
        self.infolabel=Label(self.master,text="Info:",bg='red')
        self.infolabel.grid(row=1,column=0,columnspan=5,sticky=W+E+N+S,padx=5, pady=5)
        self.E1.focus_set()
        self.E1.bind("<Return>",self.change1)
        self.E2.bind("<Return>",self.change2)
        
        tv=ttk.Treeview(self.framex)
        tv['columns']=('Rack','Pos')
        tv.heading("#0", text='ID', anchor="e")
        tv.column("#0", anchor="e",width=40)
        tv.heading('Rack', text='Rack id')
        tv.column('Rack', anchor='center', width=215)
        tv.heading('Pos', text='Pack id')
        tv.column('Pos', anchor='center', width=215) 
        tv.pack(side=LEFT,fill='x')
        
        vsb = ttk.Scrollbar(self.framex, orient="vertical", command=tv.yview)
        vsb.pack(side=RIGHT, fill='y')

        self.framex.grid(columnspan=5,sticky=W+E+N+S,padx=5, pady=5)
        
        #self.grid_rowconfigure(0, weight = 1)
        #self.grid_columnconfigure(0, weight = 1)
        
        #id list for trace back later
        self.ids=[]
        tv.tag_configure("newitem", background='white')
        tv.tag_configure("working", background='blue')
        tv.tag_configure("success", background='lawn green')
        self.treeview = tv
        self.userlabel=Label(self.master,text=username).grid(row=3,sticky=W,padx=5, pady=5)
        locations=["안양","일죽","청주","안성","NTI"]
        
        variable=StringVar(self.master)
        variable.set(locations[userlocation])
        self.warehouselistbox = apply(OptionMenu,(self.master,variable)+tuple(locations))
        
        self.warehouselistbox.grid(row=3,column=1,sticky=W,padx=5, pady=5)
        
        logging.info("Init finish")
        
    def change1(self,event):
        self.clearall(self.E1.get)
        self.E2.focus_set()
        
        
    def change2(self,event):
        self.clearall(self.E1.get)
        self.hello()
        
        
    def clearall(self,v):
        if v=='reset':
            self.E1.delete(0,last='end')
            self.E2.delete(0,last='end')
            self.E1.focus_set()
        
    def hello(self):
        if len(self.E1.get()) <1 or len(self.E2.get()) <1:
            return
        p=self.E1.get()
        r=self.E2.get()
        self._idcounter = self._idcounter  +1
        treeviewrow=self.treeview.insert("", 0, text=str(self._idcounter ), values=(p,r),tags=('newitem',)) 
        self.ids.append(treeviewrow)
        datapack=(p,r,treeviewrow)
        queuelock.acquire()        
        send_queue.put(datapack)
        queuelock.release()        
        self.infolabel.config(text="Pack: "+self.E1.get()+" at: "+self.E2.get())
        self.E1.delete(0,last='end')
        self.E2.delete(0,last='end')
        self.E1.focus_set()
        
         
def is_connection_live():
    
    # Ping parameters as function of OS
    parameters = "-n 1" if system_name().lower()=="windows" else "-c 1"
    
    # Pinging
    if system_call("ping " + parameters + " " + hostname) == 0:
        print "pass"
        return True
    else:
        print "dis"
        
        return False   


def send_data(mid,rackid,packageid):
    print("Log_send_data: \nRackid: " + rackid+" \nPackid: "+packageid)
    if not is_connection_live():
        print "Server is not available!!!"
        return False
    print "start send package"
    if len(rackid)==0 or len(packageid)==0:
        print "no data - return"
        return False
    
    
    headers = {'Content-type': 'application/json'}       
        
    datas = {'mid':mid,'rackid':rackid,'packid':packageid}
    datas=json.dumps(datas)
    #myrequest = requests.post(url,data=datas,headers=headers)
    myrequest = requests.post(url,json=datas,headers=headers)
    print('response:' + myrequest.text)
    if myrequest.text=="done":
        return True
    else:
        return False
def ask_quit():
    global exitFlag
    count=0
    for item in my_gui.treeview.get_children():
        print my_gui.treeview.item(item)['tags']
        
        if str(my_gui.treeview.item(item)['tags']) == 'success':
            count+=1
    msg="You want to quit now?"
    if count <> len(my_gui.treeview.get_children()):
        msg='Go to wifi zone first! force shutdown result in lost data finish %d/%d',(count,len(my_gui.treeview.get_children()))
    if tkMessageBox.askokcancel("Quit", msg):
        queuelock.acquire()        
        exitFlag=1
        
        queuelock.release()
        print "quit" +str(exitFlag)
        sendMessthread.join()
        root.destroy()

class userlogin:
    def __init__(self,master):
        self.master=master
        master.title("Login")  
        
        self.ul=Label(self.master,text="User name:").grid(sticky=W,padx=5,pady=5)
        self.username=Entry(self.master,width=30)
        self.username.grid(row=0,column=1, sticky=W,padx=5,pady=5)
        
        #self.pl=Label(self.master,text="Password:").grid(row=1,column=0,sticky=W,padx=5,pady=5)
        #self.password=Entry(self.master,width=30, show='*')
        #self.password.grid(row=1,column=1, sticky=W,padx=5,pady=5)
        
        #binding
        self.username.bind("<Return>",self.change1)
        #self.password.bind("<Return>",self.change2)
        
        #self.btn11 = Button(self.master,text="Ok",command = self.logincheck).grid(row=0, column=2, rowspan=2,padx=5,pady=5)
        self.btn11 = Button(self.master,text="Ok",command = self.logincheck).grid(row=0, column=2,padx=5,pady=5)
        self.username.focus_set()
        
    def logincheck(self):
        # get username , pw, and location from database here
        #cnx = mysql.connector.connect(user="root",password="213", database='warehouse')
        #cursor = cnx.cursor()
    
        #cursor.execute( " SELECT user, pass, location FROM userlist where user=%s and pass=%s;",(username,password))
        #rows = cursor.fetchall()
        #if len(rows)==1:
        pw=[('admin','123')]
        username='admin'
        userlocation=1
        if (self.username.get(),'123') in pw:
            
            loginsuccess(username,userlocation)
        else:
            self.username.delete(0,last='end')
            self.password.delete(0,last='end')
            self.username.focus_set()
            tkMessageBox.showinfo("Wrong1", "Wrong username/password")
    def change1(self,event):        
        #self.password.focus_set()
        self.logincheck()
        
    def change2(self,event):  
        self.logincheck()
            
def loginsuccess(username,userlocation):
    print "meowwwwwwwwwwwwwwwwwww"
    global root
    global my_gui
    global sendMessthread
    root.destroy()
    root=Tk()
    my_gui=userUI(root,username,userlocation)
    w = 500 # width for the Tk root
    h = 340 # height for the Tk root
    
    # get screen width and height
    ws = root.winfo_screenwidth() # width of the screen
    hs = root.winfo_screenheight() # height of the screen
    
    # calculate x and y coordinates for the Tk root window
    x = (ws/2) - (w/2)
    y = (hs/2) - (h/2)
    
    # set the dimensions of the screen 
    # and where it is placed
    
    sendMessthread.start()
    
    root.geometry('%dx%d+%d+%d' % (w, h, x, y))
    root.protocol("WM_DELETE_WINDOW", ask_quit)
    root.mainloop()
    
root = Tk() 
my_gui = userlogin(root)
w = 350 # width for the Tk root
h = 80 # height for the Tk root

# get screen width and height
ws = root.winfo_screenwidth() # width of the screen
hs = root.winfo_screenheight() # height of the screen

# calculate x and y coordinates for the Tk root window
x = (ws/2) - (w/2)
y = (hs/2) - (h/2)

# set the dimensions of the screen 
# and where it is placed
sendMessthread = sendmessage('Thread 1',1,send_queue)

root.geometry('%dx%d+%d+%d' % (w, h, x, y))
#root.protocol("WM_DELETE_WINDOW", ask_quit)
root.mainloop()

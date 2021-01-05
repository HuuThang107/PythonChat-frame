import ast
import sys
import socket
import sqlite3
import datetime
import json
import time
from random import randint
import threading
import hashlib

myLock = threading.Lock() # Khoa luong khi co su chuyen luong

class chatDB:
	global ketnoi
	global conn
	t={}
 	def __init__(self, path, createNew=False):
		"""Init chatdb
		Connect to database (at PATH) or create new one if CREATENEW = True
		"""
		self.conn = sqlite3.connect(path,check_same_thread =False)
		self.ketnoi = self.conn.cursor()
		if(createNew):
			
			self.ketnoi.execute('''CREATE TABLE USERS
									  (
									  USER 			   TEXT  PRIMARY KEY  NOT NULL,
									  PWS              TEXT    NOT NULL,
									  STATUS           TEXT    NOT NULL)''')
			
			self.ketnoi.execute('''CREATE TABLE MSGS
									 (
									 Sender              TEXT	NOT NULL,
									 Receiver            TEXT	NOT NULL,
									 Timestamp           TEXT	NOT NULL,
									 Content			 TEXT	NOT NULL,
									 Read            	 TEXT	NOT NULL)''') 
			
			self.ketnoi.execute('''CREATE TABLE COOKIES
									  (
									  COOKIE             TEXT	PRIMARY KEY	NOT NULL,
									  USER               TEXT	NOT NULL,
									  LAST_ACC           TEXT	NOT NULL)''')
		
		
		#print "Opened database successfully";
		
		# DANG XUAT TAT CA TAI KHOAN DA DANG NHAP O PHIEN LAM VIEC TRUOC
		self.ketnoi.execute("DELETE FROM COOKIES")
		self.ketnoi.execute("update Users set Status='off' ")
		print "DA LAM SACH COOKIES!"
		
	    
	def start(self):
		"""Start background tasks of chat db.
		
		Background tasks: cookie cleaner
		"""
		'''for cookie_ in self.ketnoi.execute("select Cookie from Cookies").fetchall():
			self.t[cookie_[0]]=time.time()'''
		threading.Thread(target=self.autoClear,args=()).start()
		print "MO LUONG DON COOKIES THANH CONG!"

		pass
	def stop(self, pwsr):
		"""Stop background tasks of chat db.
		
		Background tasks: cookie cleaner
		"""
		# You have to implement this method
		
		pass
		
	def autoClear(self):
		"""
		Clear inactive cookie. Timeout = 600
		Should be called in self.start
		"""
		# You have to implement this method
		while True:
			list_logout=[] # Dang xuat khi timeout = 600
			myLock.acquire(True)
			# Tim cookie co thoi gian bang 600 sau do luu vao danh danh sach
			for cookies_ in self.t:
				if(time.time()-self.t[cookies_]>=600):
					list_logout.append(cookies_)
			# Thoat cac user trong dsach log_out
			for i in list_logout:
				self.logout(i)
				print "<--Run Auto Clear Cookies KickOut Acc !--> ",time.strftime("%y-%m-%d %H:%M:%S",time.localtime())
			# Xoa danh sach log_out
			list_logout = []
			
			#time.sleep(0.05)
			myLock.release()
		pass
		
class ThreadedServer:
	def __init__(self, host, port):
		self.host = host
		self.port = port
		self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		self.sock.bind((self.host, self.port))
		

	def listen(self, maxClient):
		self.sock.listen(maxClient)
		dem = 0
		while True:
			client, address = self.sock.accept()
			dem = dem + 1
			print "KET NOI THU ",dem," DEN SERVER!"
			threading.Thread(target=self.listenToClient,args=(client, address)).start()
			
			
			
	def listenToClient(self, client, address):
		recvBuf = ''
		while True:
			data = self.recvLine(client, recvBuf)
			print data
			try:
				s = ast.literal_eval(data)
				Check_chuyendoi = "True"
			except:
				Check_chuyendoi = "False"
			
			myLock.acquire(True)
			if ( (Check_chuyendoi == "True") and ((type(s) == tuple) or (type(s) == list))):
				request = ast.literal_eval(data)
				if ((request[0]=='ONLINE') or 
					(request[0]=='ALL') or
					(request[0]=='GET') or
					(request[0]=='NEW') or
					(request[0]=='SEND') or
					(request[0]=='REG') or 
					(request[0]=='LOGIN') or
					(request[0]=='LOGOUT') or
					(request[0]=='VIEW')
					): response = self.processRequest(request)
				else:
					response = "Lenh ban gui len server khong ton tai! "
			else : response = "Lenh ban gui len server khong ton tai! "
			myLock.release()
			
				# convert any type of response to string representation
			data = str(response)
			try:
				client.send(data+'\n')
			except err:
				client.close()
					
				return  

	def recvLine(self, client, recvBuf):  # receive line from client
		while '\n' not in recvBuf:
			try:
				data = client.recv(1024)
				if data:
					recvBuf += data
				# else:
				#     return [False, 'disconnected']
			except:
				client.close()
				return [False, 'error']
		lineEnd = recvBuf.index('\n')
		data = recvBuf[:lineEnd]
		recvBuf = recvBuf[lineEnd+1:]
		return data

	def processRequest(self, request):
		global chatdb
		"""Process a request of a client
		
		A request is in the form:
			['ONLINE'] => getOnlineUsers
			['ALL'] => getAllUsers
			['GET', cookie, usr2] => getAllMsgs
			['NEW', cookie, frm] => getNewMsgs
			['SEND', cookie, to, content] => sendMsg
			['REG', usr, wd] => register
			['LOGIN', usr, wd] => login
			['LOGOUT', cookie] => logout
		"""
		# You have to implement this method
		if(request[0]=='ONLINE'): return chatdb.getOnlineUsers()
		if(request[0]=='ALL'): return chatdb.getAllUsers()
		if(request[0]=='GET'): return chatdb.getAllMsgs(request[1],request[2])
		if(request[0]=='NEW'): return chatdb.getNewMsgs(request[1],request[2])
		if(request[0]=='SEND'):  return chatdb.sendMsg(request[1],request[2],request[3])
		if(request[0]=='REG'): return chatdb.register(request[1],request[2])
		if(request[0]=='LOGIN'): return chatdb.login(request[1],request[2])
		if(request[0]=='LOGOUT'): return chatdb.logout(request[1])
		if(request[0]=='VIEW'): return chatdb.view(request[1]) 
		pass


chatdb = None
if __name__ == "__main__":
	if len(sys.argv) != 4:
		print "Usage: %s <port> <dbFile> <createNew>" % sys.argv[0]
		print "Example: %s 8081 chat.sqlite new" % sys.argv[0]
		exit(1)
	port = int(sys.argv[1])
	dbFile = sys.argv[2]
	createNew = sys.argv[3]
	if createNew == 'new':
		createNew = True
	else:
		createNew = False
	chatdb = chatDB(dbFile, createNew)
	print "DATABASE DA KET NOI THANH CONG!"
	chatdb.start()
	ThreadedServer('192.168.0.103', port).listen(50)
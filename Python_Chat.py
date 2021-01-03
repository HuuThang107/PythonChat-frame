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
		print "MO LUONG DON COOKIE THANH CONG!"

		pass
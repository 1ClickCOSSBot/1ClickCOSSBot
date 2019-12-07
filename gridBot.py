from pycoss import PyCOSSClient
import os.path
import datetime
import time
import pickle
import requests
import tkinter as tk
from tkinter import messagebox

class gridBotStart:

	def __init__(self):
		#Create pycoss object with API keys
		with open('gridSettings.conf', 'rb') as f:  # Python 3: open(..., 'rb')
			    quotePair, tradePair, publicKey, privateKey, orderSize, gridDistance, lowerPrice, higherPrice, numberOfGrids = pickle.load(f)
		self.coss_client = PyCOSSClient(api_public=publicKey,
		                           api_secret=privateKey)

	def sendTelegram(token, chatID, message):
		messageSender = 'https://api.telegram.org/bot' + token + '/sendMessage?chat_id=' + chatID + '&parse_mode=Markdown&text=' + message
		response = requests.get(messageSender)
		return response.json()

	def updateRunHistory(message, fileName = "history", firstMessage = "no"):
		print(message)
		print
		deleteFile = "no"
		if os.path.exists(fileName + ".txt") and firstMessage != "no":
			print("Previous instance of history file eixsts")
			temp = tk.Tk()
			temp.withdraw()
			deleteFile = tk.messagebox.askquestion("File Exists", "A previous instance of bot history exists, would you like to delete it?")

		if deleteFile != "yes":
			f = open(fileName + ".txt", "a+")
			message = "\n" + message
		else:
			f = open(fileName + ".txt", "w+")
		if firstMessage == "no":
			message = "\n" + message
		f.write(message)
		f.close()

	def saveOrders(orders):
		#Check if database file already exists, if file exists ask user if they would like to cancel all previous orders and start over
		print("Adding new order to orderDb.txt")
		with open('orderDb.pickle', 'wb') as handle:
			pickle.dump(orders, handle, protocol=pickle.HIGHEST_PROTOCOL)

	def loadOrders():
		orders = 0
		print("Loading orders")
		with open('orderDb.pickle', 'rb') as handle:
			orders = pickle.load(handle)
		return orders

	def checkOldOrders():
		#Check if an old order file exists
		if os.path.exists("orderDb.pickle"):
			return True
		else:
			return False

	def gridStart(instanceName):
		#Get Telegram settings
		with open('telegramSettings.conf', 'rb') as f:  # Python 3: open(..., 'rb')
			telegramEnabled, getTelegramToken, getTelegramChatID = pickle.load(f)

		#Notify User of bot instance in telegram
		if telegramEnabled:
			gridBotStart.sendTelegram(getTelegramToken, getTelegramChatID, instanceName.strip() + ":\nStarting grid MM strategy")

		#Clear any previous history and add new history
		gridBotStart.updateRunHistory(instanceName.strip() + ":\nStarting grid MM strategy", "history", "yes")

		#Check if any previous instance of the bot was running and update order history
		if gridBotStart.checkOldOrders():
			print("Previous orders exist canceling them now")
			#Load orders and then cancel them one by one
			loadOrdersToCancel = gridBotStart.loadOrders()
			for orders in loadOrdersToCancel:
				print("Deleting order")

		#Load strategy settings
		

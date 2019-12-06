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

	def updateOrderDatabase(message, restart = "no"):
		#Check if database file already exists, if file exists ask user if they would like to cancel all previous orders and start over
		orderFileRead = open('existingOrders.txt', "r")
		deleteOrders = "yes"
		if orderFileRead.mode == "r":
			deleteOrders = tk.messagebox.askquestion("Bot orders exist", "Would you like to delete all previous orders created by this bot instance or continue from the previous position?")
		orderFileRead.close()

		if deleteOrders == "yes":
			print("Cancelling all orders from previous instance and starting over")

	def checkOldOrders():
		#Check if an old order file exists
		if os.path.exists("orderDb.txt"):
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
		if checkOldOrders():
			print("Looks like a previous instance of this bot has some open orders")
		else:
			print("Creating order database")
	
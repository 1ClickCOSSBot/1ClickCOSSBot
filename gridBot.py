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

	def updateRunHistory(self, message, fileName = "history", firstMessage = "No"):
		deleteFile = "No"
		if os.path.exists(fileName + ".txt") and firstMessage != "No":
			print("Dude this file eixsts")
			temp = tk.Tk()
			temp.withdraw()
			deleteFile = tk.messagebox.askquestion("File Exists", "This file exists, would you like to delete it?")

		if deleteFile != "yes":
			f = open(fileName + ".txt", "a+")
		else:
			f = open(fileName + ".txt", "w+")
		f.write(message)
		f.close()

	def gridStart(instanceName):
		#Get Telegram settings
		with open('telegramSettings.conf', 'rb') as f:  # Python 3: open(..., 'rb')
			telegramEnabled, getTelegramToken, getTelegramChatID = pickle.load(f)

		#Notify User of bot instance in telegram
		if telegramEnabled:
			gridBotStart.sendTelegram(getTelegramToken, getTelegramChatID, instanceName.strip() + ":\nStarting grid MM strategy")

		#Clear any previous history and add new history
		gridBotStart.updateRunHistory(instanceName.strip() + ":\nStarting grid MM strategy")

		#Check if database file already exists, if file exists ask user if they would like to cancel all previous orders and start over
		orderFile = open('existingOrders.txt', "r")
		if orderFile.mode == "r":
			deleteOrders = tk.messagebox.askquestion("Bot orders exist", "Would you like to delete all previous orders created by this bot instance or continue from the previous position?")

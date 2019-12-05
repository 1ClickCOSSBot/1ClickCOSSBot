from pycoss import PyCOSSClient
import datetime
import time
import pickle
import requests

class gridBotStart:

	def __init__(self):
		#Create pycoss object with API keys
		with open('gridSettings.conf', 'rb') as f:  # Python 3: open(..., 'rb')
			    tradePair, publicKey, privateKey, orderSize, gridDistance, lowerPrice, higherPrice, numberOfGrids = pickle.load(f)
		self.coss_client = PyCOSSClient(api_public=publicKey,
		                           api_secret=privateKey)

	def sendTelegram(token, chatID, message):
		messageSender = 'https://api.telegram.org/bot' + token + '/sendMessage?chat_id=' + chatID + '&parse_mode=Markdown&text=' + message
		response = requests.get(messageSender)
		return response.json()

	def updateRunHistory(message):
		print("Hello")	

	def gridStart(instanceName):
		#Get Telegram settings
		with open('telegramSettings.conf', 'rb') as f:  # Python 3: open(..., 'rb')
			telegramEnabled, getTelegramToken, getTelegramChatID = pickle.load(f)

		#Notify User of bot instance in telegram
		if telegramEnabled:
			gridBotStart.sendTelegram(getTelegramToken, getTelegramChatID, instanceName.strip() + ":\nStarting grid MM strategy")

		#Clear any previous history and add new history
		gridBotStart.updateRunHistory(instanceName.strip() + ":\nStarting grid MM strategy")
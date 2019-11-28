from pycoss import PyCOSSClient
import datetime
import time
import pickle
import requests

class gridBotStart:

	def sendTelegram(token, chatID, message):
		messageSender = 'https://api.telegram.org/bot' + token + '/sendMessage?chat_id=' + chatID + '&parse_mode=Markdown&text=' + message
		response = requests.get(messageSender)
		return response.json()

	def updateRunHistory(message):
		print(message)

	def gridStart(instanceName):
		#Grab settings from gridSettings.conf
		#publicKey, privateKey, orderSize, gridDistance, lowerPrice, higherPrice, numberOfGrids
		with open('gridSettings.conf', 'rb') as f:  # Python 3: open(..., 'rb')
		    tradePair, publicKey, privateKey, orderSize, gridDistance, lowerPrice, higherPrice, numberOfGrids = pickle.load(f)

		print("Trading Pair is: " + tradePair)
		print("Public Key is: " + publicKey)
		print("Private Key is: " + privateKey)
		print("Order Size is: " + orderSize)
		print("Seperation between grids is: " + gridDistance)
		print("Lower grid price is: " + lowerPrice)
		print("Upper grid price is: " + higherPrice)
		print("Number of grids are: " + str(numberOfGrids))

		coss_client = PyCOSSClient(api_public=publicKey,
		                           api_secret=privateKey)

		#coss_ob = coss_client.get_order_book(symbol="COS_ETH")
		#print("Price: " + coss_ob["bids"][1][0] + " Amount: " + coss_ob["bids"][0][1])

		#Get Telegram settings
		with open('telegramSettings.conf', 'rb') as f:  # Python 3: open(..., 'rb')
			telegramEnabled, getTelegramToken, getTelegramChatID = pickle.load(f)

		#Notify User of bot instance in telegram
		if telegramEnabled:
			gridBotStart.sendTelegram(getTelegramToken, getTelegramChatID, instanceName.strip() + ":\nStarting grid MM strategy")

		#Clear any previous history and add new history
		
		gridBotStart.updateRunHistory(instanceName.strip() + ":\nStarting grid MM strategy")			

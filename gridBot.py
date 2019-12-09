from pycoss import PyCOSSClient
import os.path
import datetime
import time
import pickle
import requests
import tkinter as tk
import exchange
from exchange import exchangeInfo
from tkinter import messagebox

class gridBotStart:

	def sendTelegram(message):
		#Get Telegram settings
		with open('telegramSettings.conf', 'rb') as f:  # Python 3: open(..., 'rb')
			telegramEnabled, token, chatID = pickle.load(f)
		if telegramEnabled:
			messageSender = 'https://api.telegram.org/bot' + token + '/sendMessage?chat_id=' + chatID + '&parse_mode=Markdown&text=' + message
			response = requests.get(messageSender)
			return response.json()
		return False

	def updateRunHistory(message, fileName = "history", firstMessage = "no"):
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
			message = message
		f.write(message)
		f.close()

	def saveOrders(orders):
		#Check if database file already exists, if file exists ask user if they would like to cancel all previous orders and start over
		with open('orderDb.pickle', 'wb') as handle:
			pickle.dump(orders, handle, protocol=pickle.HIGHEST_PROTOCOL)

	def loadOrders():
		orders = 0
		with open('orderDb.pickle', 'rb') as handle:
			orders = pickle.load(handle)
		return orders

	def gridStart(instanceName):

		#Hide tkinter UI window to show error messages or popup questions
		root = tk.Tk()
		root.withdraw()

		#Create pycoss object with API keys and load strategy settings
		with open('gridSettings.conf', 'rb') as f:
			    quotePair, tradePair, publicKey, privateKey, orderSize, gridDistance, lowerBuyPrice, higherBuyPrice, lowerSellPrice, higherSellPrice, numberOfGrids = pickle.load(f)
		pyCossClient = PyCOSSClient(api_public=publicKey,
		                           api_secret=privateKey)

		#Get Telegram settings
		with open('telegramSettings.conf', 'rb') as f:  # Python 3: open(..., 'rb')
			telegramEnabled, getTelegramToken, getTelegramChatID = pickle.load(f)

		#Notify User of bot instance in telegram
		gridBotStart.sendTelegram(instanceName.strip() + ":\nStarting grid MM strategy")
		#Clear any previous history and add new history
		gridBotStart.updateRunHistory(instanceName.strip() + ":\nStarting grid MM strategy", "history", "yes")

		#Check if any previous instance of the bot was running and update order history
		if os.path.exists("orderDb.pickle"):
			os.remove("orderDb.pickle")
			print("Previous orders exist canceling them now")
			#Load orders and then cancel them one by one
			#loadOrdersToCancel = gridBotStart.loadOrders()
			#for orders in loadOrdersToCancel:
			#	print("Deleting order and exiting: Temp TEST")
			#	exit(0)
		
		#Store grid count
		numberGrids = int(float(numberOfGrids)/2)
		if numberOfGrids <= 2:
			orderString = "order"
		else:
			orderString = "orders"
		gridBotStart.sendTelegram(str(numberGrids) + " " + orderString + " will be placed on buy side")
		gridBotStart.sendTelegram(str(numberGrids) + " " + orderString + " will be placed on sell side")
		gridBotStart.updateRunHistory(str(numberGrids) + " " + orderString + " will be placed on buy side")
		gridBotStart.updateRunHistory(str(numberGrids) + " " + orderString + " will be placed on sell side")
		

		orderType = "limit"
		orderPair = tradePair + "_" + quotePair
		allOrders = []

		#Create buy orders for specified grids
		buyCount = 1
		orderBuyStartPrice = higherBuyPrice
		orderBuySide = "BUY"
		while buyCount <= numberGrids:
			myOrder = pyCossClient.create_order(orderPair, orderBuySide, orderType, orderSize, orderBuyStartPrice)
			if "error" in myOrder:
				print("Some error was encountered when trying to create buy order#" + str(buyCount) + " with price " + str(orderBuyStartPrice) + " " + quotePair + ". Bot will exit")
				tk.messagebox.showinfo("Error creating buy order!", "Some error was encountered when creating a buy order, please ensure you have enough balance and you are above the minimum threshold for the trading pair.")
				exit(0)
			allOrders.append(myOrder)
			gridBotStart.sendTelegram("Buy order " + str(buyCount) + " created at " + str(orderBuyStartPrice) + " " + quotePair)
			gridBotStart.updateRunHistory("Buy order #" + str(buyCount) + " created at " + str(orderBuyStartPrice) + " " + quotePair)
			orderBuyStartPrice = float(orderBuyStartPrice) - float(gridDistance)
			buyCount = buyCount + 1
			

		#Create sell orders for specified grids
		sellCount = 1
		orderSellStartPrice = lowerSellPrice
		orderSellSide = "SELL"
		while sellCount <= numberGrids:
			myOrder = pyCossClient.create_order(orderPair, orderSellSide, orderType, orderSize, orderSellStartPrice)
			if "error" in myOrder:
				print("Some error was encountered when trying to create sell order#" + str(sellCount) + " with price " + str(orderSellStartPrice) + " " + quotePair + ". Bot will exit")
				tk.messagebox.showinfo("Error creating sell order!", "Some error was encountered when creating a sell order, please ensure you have enough balance and you are above the minimum threshold for the trading pair.")
				exit(0)
			allOrders.append(myOrder)
			gridBotStart.sendTelegram("Sell order " + str(buyCount) + " created at " + str(orderSellStartPrice) + " " + quotePair)
			gridBotStart.updateRunHistory("Sell order #" + str(sellCount) + " created at " + str(orderSellStartPrice) + " " + quotePair)
			orderSellStartPrice = float(orderSellStartPrice) + float(gridDistance)
			sellCount = sellCount + 1

		#Save all the orders
		gridBotStart.saveOrders(allOrders)

		#Load another instance of exchange API
		myExchange = exchangeInfo()

		#Check all orders and update as necessary in permanent while loop every 5 seconds
		while True:
			#Load orders and check status of each order. If order is completed create a new order on opposite side of grid. Make sure orders are within price range
			loadAndCheckOrders = gridBotStart.loadOrders()
			orderCount = 1
			count = 0
			for orders in loadAndCheckOrders:
				print("Checking order #" + str(orderCount))
				currentStatus = pyCossClient.get_order_details(orders['order_id'])
				if str(currentStatus['status']) == "open":
					print("Order " + str(orderCount) + " is still open")
				elif str(currentStatus['status']) == "filled":
					#Get latest ask and bid prices to ensure we are not placing orders on wrong side
					latestAskBid = myExchange.getPairAskBid(quotePair, tradePair)
					price = 0
					print("Order " + str(orderCount) + " completed. Creating new order on opposite side.")
					if str(currentStatus['order_side']) == "SELL":
						orderSide = "BUY"
						buyPrice = float(currentStatus['order_price']) - float(gridDistance)
						if buyPrice >= float(latestAskBid[0]):
							price = float(latestAskBid[0]) - float(gridDistance)
						else:
							price = buyPrice
					else:
						orderSide = "SELL"
						sellPrice = float(currentStatus['order_price']) + float(gridDistance)
						if sellPrice <= float(latestAskBid[1]):
							price = float(latestAskBid[1]) + float(gridDistance)
						else:
							price = sellPrice
					if orderSide == "SELL" and price >= float(lowerSellPrice) and price <= float(higherSellPrice):
						newOrder = pyCossClient.create_order(orderPair, orderSide, orderType, orderSize, price)
						loadAndCheckOrders[count] = newOrder
						gridBotStart.sendTelegram("Buy order " + str(orderCount) + " completed. Creating sell order on opposite grid")
						gridBotStart.updateRunHistory("Buy order " + str(orderCount) + " completed. Creating sell order on opposite grid")
						gridBotStart.sendTelegram("Sell order " + str(orderCount) + " created at " + str(price) + " " + quotePair)
						gridBotStart.updateRunHistory("Sell order " + str(orderCount) + " created at " + str(price) + " " + quotePair)
					elif orderSide == "BUY" and price >= float(lowerBuyPrice) and price <= float(higherBuyPrice):
						newOrder = pyCossClient.create_order(orderPair, orderSide, orderType, orderSize, price)
						loadAndCheckOrders[count] = newOrder
						gridBotStart.sendTelegram("Sell order " + str(orderCount) + " completed. Creating buy order on opposite grid")
						gridBotStart.updateRunHistory("Sell order " + str(orderCount) + " completed. Creating buy order on opposite grid")
						gridBotStart.sendTelegram("Buy order " + str(orderCount) + " created at " + str(price) + " " + quotePair)
						gridBotStart.updateRunHistory("Buy order " + str(orderCount) + " created at " + str(price) + " " + quotePair)
					else:
						print("Price doesn't fall within your specified price range")
				orderCount = orderCount + 1
				count = count + 1
				time.sleep(2)
			gridBotStart.saveOrders(loadAndCheckOrders)
			print("\nCheck completed. Waiting 5 seconds and checking again\n")
			time.sleep(3)
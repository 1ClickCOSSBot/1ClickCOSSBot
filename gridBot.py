from pycoss import PyCOSSClient
import os.path
import datetime
import time
import pickle
import requests
import tkinter as tk
import exchange
import sys
from sys import exit
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

	def cancelOrders(client, allOrders):
		for orders in allOrders:
			try:
				client.cancel_order(orders['order_id'], orders['order_symbol'])
				print("Attempting to cancel an order")
			except:
				print("Something went wrong cancelling one of the orders")
				continue
			print("Success!")

	def floatToStr(originalNumber):
		actualNumber = float(originalNumber)
		decimalCount = 0
		while actualNumber < 1:
			actualNumber = actualNumber * 10
			decimalCount = decimalCount + 1

		if float(originalNumber) <= 1:
			myString = "0."
			for i in range(decimalCount-1):
				myString = myString + "0" 
			myString = myString + str(int(float(originalNumber) * (10**(decimalCount+3))))
		else:
			myString = str(actualNumber)
		return myString

	def gridStart(instanceName):

		#Hide tkinter UI window to show error messages or popup questions
		root = tk.Tk()
		root.withdraw()

		#Create pycoss object with API keys and load strategy settings
		with open('gridSettings.conf', 'rb') as f:
			    quotePair, tradePair, publicKey, privateKey, orderSize, gridDistance, lowerBuyPrice, higherBuyPrice, lowerSellPrice, higherSellPrice, numberOfGrids = pickle.load(f)
		pyCossClient = PyCOSSClient(api_public=publicKey,
		                           api_secret=privateKey)

		#Load another instance of exchange API
		myExchange = exchangeInfo()

		#Get Telegram settings
		with open('telegramSettings.conf', 'rb') as f:  # Python 3: open(..., 'rb')
			telegramEnabled, getTelegramToken, getTelegramChatID = pickle.load(f)

		#Keep track of total profit
		totalProfit = 0
		if not os.path.exists("totalProfit.pickle"):
			with open('totalProfit.pickle', 'wb') as f:
				pickle.dump([totalProfit], f)

		#Check if any previous instance of the bot was running and update order history
		skipSetup = False
		if os.path.exists("orderDb.pickle"):
			print("Previous orders exist")
			resumeBot = tk.messagebox.askquestion("Resume Previous Instance", "A previous instance of this bot was found, would you like to continue from there?")
			if resumeBot == 'yes':
				print("Continuing from previous orders")
				skipSetup = True
				with open('totalProfit.pickle', 'rb') as f:
					resumeProfit = pickle.load(f)
				totalProfit = float(resumeProfit[0])
			else:
				skipSetup = False
				print("Deleting and attempting to cancel previous orders!")
				myOrders = gridBotStart.loadOrders()
				gridBotStart.cancelOrders(pyCossClient, myOrders)
				os.remove("orderDb.pickle")
		
		#Setup order type settings
		orderType = "limit"
		orderPair = tradePair + "_" + quotePair
		allOrders = []

		#Get allowed decimal places for price 
		decimalLimit = myExchange.getPairDecimal(orderPair)

		if not skipSetup:
			#Notify User of bot instance in telegram
			gridBotStart.sendTelegram(instanceName.strip() + ":\nStarting grid MM strategy")
			#Clear any previous history and add new history
			gridBotStart.updateRunHistory(instanceName.strip() + ":\nStarting grid MM strategy", "history", "yes")

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
			

			#Create buy orders for specified grids
			buyCount = 1
			orderBuyStartPrice = round(float(higherBuyPrice), decimalLimit)
			orderBuySide = "BUY"
			while buyCount <= numberGrids:
				myOrder = {'error':'temp'}
				try:
					myOrder = pyCossClient.create_order(orderPair, orderBuySide, orderType, orderSize, round(orderBuyStartPrice, decimalLimit))
				except:
					print("Failed to access exchange when attempting to create order!")
					tk.messagebox.showinfo("Failed to connect to exchange when creating order!")
					if buyCount > 1:
						gridBotStart.cancelOrders(pyCossClient, allOrders)
					exit(0)
				if "error" in myOrder:
					print("Some error was encountered when trying to create buy order#" + str(buyCount) + " with price " + gridBotStart.floatToStr(round(orderBuyStartPrice, decimalLimit)) + " " + quotePair + ".\n\nError Description from Exchange:\n" + myOrder['error_description'] + "\nYour total: Size("+ gridBotStart.floatToStr(orderSize) +") * Price("+ gridBotStart.floatToStr(round(orderBuyStartPrice,decimalLimit)) +") = " + gridBotStart.floatToStr((float(orderSize)*float(orderBuyStartPrice))) + "\nCancelling orders and stopping, please check your strategy!")
					tk.messagebox.showinfo("Error creating buy order!", "Some error was encountered when creating a buy order, please ensure you have enough balance and you are above the minimum threshold for the trading pair.\n\nError Description from Exchange:\n" + myOrder['error_description'] + "\nYour total: Size("+ gridBotStart.floatToStr(orderSize) +") * Price("+ gridBotStart.floatToStr(round(orderBuyStartPrice,decimalLimit)) +") = " + gridBotStart.floatToStr((float(orderSize)*float(orderBuyStartPrice))) + "\nCancelling orders and stopping, please check your strategy!")
					if buyCount > 1:
						gridBotStart.cancelOrders(pyCossClient, allOrders)
					exit(0)
				myOrder['grid_status'] = 'open'
				myOrder['start_price'] = gridBotStart.floatToStr(round(orderBuyStartPrice, decimalLimit))
				myOrder['prev_price'] = 0
				allOrders.append(myOrder)
				gridBotStart.sendTelegram("Buy order " + str(buyCount) + " created at " + gridBotStart.floatToStr(round(orderBuyStartPrice, decimalLimit)) + " " + quotePair)
				gridBotStart.updateRunHistory("Buy order #" + str(buyCount) + " created at " + gridBotStart.floatToStr(round(orderBuyStartPrice, decimalLimit)) + " " + quotePair)
				orderBuyStartPrice = round(float(orderBuyStartPrice) - float(gridDistance), decimalLimit)
				buyCount = buyCount + 1
				

			#Create sell orders for specified grids
			sellCount = 1
			orderSellStartPrice = round(float(lowerSellPrice), decimalLimit)
			orderSellSide = "SELL"
			while sellCount <= numberGrids:
				myOrder = {'error':'temp'}
				try:
					myOrder = pyCossClient.create_order(orderPair, orderSellSide, orderType, orderSize, round(orderSellStartPrice, decimalLimit))
				except:
					print("Failed to access exchange when attempting to create order!")
					tk.messagebox.showinfo("Failed to connect to exchange when creating order!")
					if sellCount > 1:
						gridBotStart.cancelOrders(pyCossClient, allOrders)
					exit(0)
				if "error" in myOrder:
					print("Some error was encountered when trying to create sell order#" + str(sellCount) + " with price " + gridBotStart.floatToStr(round(orderSellStartPrice, decimalLimit)) + " " + quotePair + ".\n\nError Description from Exchange:\n" + myOrder['error_description'] + "\nYour total: Size("+ gridBotStart.floatToStr(orderSize) +") * Price("+ gridBotStart.floatToStr(round(orderSellStartPrice, decimalLimit)) +") = " + gridBotStart.floatToStr((float(orderSize)*float(orderSellStartPrice))) + "\nCancelling orders and stopping, please check your strategy!")
					tk.messagebox.showinfo("Error creating sell order!", "Some error was encountered when creating a sell order, please ensure you have enough balance and you are above the minimum threshold for the trading pair.\n\nError Description from Exchange:\n" + myOrder['error_description'] + "\nYour total: Size("+ gridBotStart.floatToStr(orderSize) +") * Price("+ gridBotStart.floatToStr(round(orderSellStartPrice, decimalLimit)) +") = " + gridBotStart.floatToStr((float(orderSize)*float(orderSellStartPrice))) + "\nCancelling orders and stopping, please check your strategy!")
					if sellCount > 1:
						gridBotStart.cancelOrders(pyCossClient, allOrders)
					exit(0)
				myOrder['grid_status'] = 'open'
				myOrder['start_price'] = gridBotStart.floatToStr(round(orderSellStartPrice, decimalLimit))
				myOrder['prev_price'] = 0
				allOrders.append(myOrder)
				gridBotStart.sendTelegram("Sell order " + str(sellCount) + " created at " + gridBotStart.floatToStr(round(orderSellStartPrice, decimalLimit)) + " " + quotePair)
				gridBotStart.updateRunHistory("Sell order #" + str(sellCount) + " created at " + gridBotStart.floatToStr(round(orderSellStartPrice, decimalLimit)) + " " + quotePair)
				orderSellStartPrice = round(float(orderSellStartPrice) + float(gridDistance), decimalLimit)
				sellCount = sellCount + 1

			#Save all the orders
			gridBotStart.saveOrders(allOrders)

		#Check all orders and update as necessary in permanent while loop every 4 seconds
		while True:
			#Load orders and check status of each order. If order is completed create a new order on opposite side of grid. Make sure orders are within price range
			loadAndCheckOrders = gridBotStart.loadOrders()
			orderCount = 1
			count = 0

			for orders in loadAndCheckOrders:
				print("Checking grid order #" + str(orderCount))
				currentStatus = None
				try:
					currentStatus = pyCossClient.get_order_details(orders['order_id'])
				except:
					print("Could not check this order due to connection issue")
					orderCount = orderCount + 1
					count = count + 1
					continue
				if 'status' in currentStatus:
					pass
				else:
					print("Could not load status from exchange will keep trying!")
					continue

				if str(currentStatus['status']) == "open":
					print("Order " + str(orderCount) + " is still open")
				elif str(currentStatus['status']) == "filled":
					#Get latest ask and bid prices to ensure we are not placing orders on wrong side
					latestAskBid = [0,0]
					try:
						latestAskBid = myExchange.getPairAskBid(quotePair, tradePair)
					except:
						print("Couldn't get orderbook from exchange!")
						orderCount = orderCount + 1
						count = count + 1
						continue
					price = 0
					print("Order " + str(orderCount) + " completed. Creating new order on opposite side.")
					if str(currentStatus['order_side']) == "SELL":
						orderSide = "BUY"
						buyPrice = round(float(orders['start_price']) - float(gridDistance), decimalLimit)
						if buyPrice >= round(float(latestAskBid[0]), decimalLimit):
							price = round(float(latestAskBid[0]) - float(gridDistance), decimalLimit)
						else:
							price = buyPrice
					else:
						orderSide = "SELL"
						sellPrice = round(float(orders['start_price']) + float(gridDistance), decimalLimit)
						if sellPrice <= round(float(latestAskBid[1]), decimalLimit):
							price = round(float(latestAskBid[1]) + float(gridDistance), decimalLimit)
						else:
							price = sellPrice
					if orderSide == "SELL" and price >= round(float(lowerBuyPrice), decimalLimit) and price <= round(float(higherSellPrice), decimalLimit):
						newOrder = None
						try:
							newOrder = pyCossClient.create_order(orderPair, orderSide, orderType, orderSize, round(price, decimalLimit))
						except:
							print("Failed to create new order because of an issue contacting the exchange. Will try again later")
							orderCount = orderCount + 1
							count = count + 1
							continue
						gridBotStart.sendTelegram("Grid order " + str(orderCount) + " (Buy @ " + gridBotStart.floatToStr(round(float(currentStatus['order_price']), decimalLimit)) + ") completed.")
						gridBotStart.updateRunHistory("Grid order " + str(orderCount) + " (Buy @ " + gridBotStart.floatToStr(round(float(currentStatus['order_price']), decimalLimit)) + ") completed.")
						gridBotStart.sendTelegram("Grid order " + str(orderCount) + " created. Sell at " + gridBotStart.floatToStr(round(float(price), decimalLimit)) + " " + quotePair)
						gridBotStart.updateRunHistory("Grid order " + str(orderCount) + " created. Sell at " + gridBotStart.floatToStr(round(float(price), decimalLimit)) + " " + quotePair)
						newOrder['prev_price'] = round(float(currentStatus['order_price']), decimalLimit)
						#Check if order was a grid completion and print profit
						if orders['grid_status'] == 'open':
							newOrder['grid_status'] = 'close'
						else:
							newOrder['grid_status'] = 'open'
							profitGenerated = abs(round(float(orders['prev_price']), decimalLimit) - round(float(currentStatus['order_price']), decimalLimit))
							totalProfit = totalProfit + (float(orderSize)*float(profitGenerated))
							gridBotStart.sendTelegram(instanceName + " Total profit: " + gridBotStart.floatToStr(totalProfit) + " " + quotePair)
							gridBotStart.updateRunHistory(instanceName + " Total profit: " + gridBotStart.floatToStr(totalProfit) + " " + quotePair)
							with open('totalProfit.pickle', 'wb') as f:
								pickle.dump([totalProfit], f)
						#Save new order
						originalPrice = round(float(orders['start_price']) + float(gridDistance), decimalLimit)
						newOrder['start_price'] = round(originalPrice, decimalLimit)
						loadAndCheckOrders[count] = newOrder
					elif orderSide == "BUY" and price >= float(lowerBuyPrice) and price <= float(higherSellPrice):
						newOrder = None
						try:
							newOrder = pyCossClient.create_order(orderPair, orderSide, orderType, orderSize, price)
						except:
							print("Failed to create new order because of an issue contacting the exchange. Will try again later")
							orderCount = orderCount + 1
							count = count + 1
							continue
						gridBotStart.sendTelegram("Grid order " + str(orderCount) + " (Sell @ " + gridBotStart.floatToStr(round(float(currentStatus['order_price']), decimalLimit)) + ") completed.")
						gridBotStart.updateRunHistory("Grid order " + str(orderCount) + " (Sell @ " + gridBotStart.floatToStr(round(float(currentStatus['order_price']), decimalLimit)) + ") completed.")
						gridBotStart.sendTelegram("Grid order " + str(orderCount) + " created. Buy at " + gridBotStart.floatToStr(round(float(price), decimalLimit)) + " " + quotePair)
						gridBotStart.updateRunHistory("Grid order " + str(orderCount) + " created. Buy at " + gridBotStart.floatToStr(round(float(price), decimalLimit)) + " " + quotePair)
						newOrder['prev_price'] = round(float(currentStatus['order_price']), decimalLimit)
						#Check if order was a grid completion and print profit
						if orders['grid_status'] == 'open':
							newOrder['grid_status'] = 'close'
						else:
							newOrder['grid_status'] = 'open'
							profitGenerated = abs(round(float(orders['prev_price']), decimalLimit) - round(float(currentStatus['order_price']), decimalLimit))
							totalProfit = totalProfit + (float(orderSize)*float(profitGenerated))
							gridBotStart.sendTelegram(instanceName + " Total profit: " + gridBotStart.floatToStr(totalProfit) + " " + quotePair)
							gridBotStart.updateRunHistory(instanceName + " Total profit: " + gridBotStart.floatToStr(totalProfit) + " " + quotePair)
							with open('totalProfit.pickle', 'wb') as f:
								pickle.dump([totalProfit], f)
						#Save new order
						originalPrice = round(float(orders['start_price']) - float(gridDistance), decimalLimit)
						newOrder['start_price'] = round(originalPrice, decimalLimit)
						loadAndCheckOrders[count] = newOrder
					else:
						print("Price doesn't fall within your specified price range")
				else:
					print("Order " + str(orderCount) + " is partially filled or cancelled")
				orderCount = orderCount + 1
				count = count + 1
				time.sleep(0.2)
			gridBotStart.saveOrders(loadAndCheckOrders)
			print("\nCheck completed. Waiting 4 seconds and checking again\n")
			time.sleep(4)
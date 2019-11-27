from pycoss import PyCOSSClient
import datetime
import time
import pickle

class gridBotStart:

	def gridStart():
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

		coss_ob = coss_client.get_order_book(symbol="COS_ETH")
		print("Price: " + coss_ob["bids"][1][0] + " Amount: " + coss_ob["bids"][0][1])

	def sendTelegram():
		print("Sending telegram message")

	def updateRunHistory():
		print("Updating run history")
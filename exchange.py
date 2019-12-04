from pycoss import PyCOSSClient
import datetime
import time
import pickle
import requests

class exchangeInfo:

	def __init__(self, getPublicKey = None, getPrivateKey=None):
		if getPublicKey is None and getPrivateKey is None:
			#Create pycoss object with API keys
			with open('gridSettings.conf', 'rb') as f:  # Python 3: open(..., 'rb')
				quotesPair, tradePair, publicKey, privateKey, orderSize, gridDistance, lowerPrice, higherPrice, numberOfGrids = pickle.load(f)
		else:
			publicKey = getPublicKey
			privateKey = getPrivateKey
		self.coss_client = PyCOSSClient(api_public=publicKey,
		                           api_secret=privateKey)

	def checkConnection(self):
		connected = self.coss_client.test_connection()
		if connected:
			return True
		else:
			return False

	def getAllPairs(self, quotePair):
		pairList = []
		exchangeInfo = self.coss_client.get_exchange_info()
		exchangeSymbols = exchangeInfo["symbols"]
		symbolCount = 0
		for allSymbols in exchangeSymbols:
			actualQuotePair = exchangeSymbols[symbolCount]["symbol"].split('_')[1]
			if actualQuotePair == quotePair:
				pairList.append(exchangeSymbols[symbolCount]["symbol"].split('_')[0])
				#print(exchangeSymbols[symbolCount]["symbol"])
			symbolCount = symbolCount + 1

		return pairList

	def testKey(self):
		try:
			self.coss_client.get_balances()
			return True
		except:
			return False

'''
myExchange = exchangeInfo()
connected = myExchange.checkConnection()
if connected:
	print("Connected")
else:
	print("Not Connected")
'''
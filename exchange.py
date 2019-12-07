from pycoss import PyCOSSClient
import datetime
import time
import pickle
import requests

class exchangeInfo:

	def __init__(self, getPublicKey = None, getPrivateKey=None):

		myPublicKey = getPublicKey
		myPrivateKey = getPrivateKey

		if getPublicKey is None and getPrivateKey is None:
			#Create pycoss object with API keys
			with open('gridSettings.conf', 'rb') as f:  # Python 3: open(..., 'rb')
				temp, temp, storedPublicKey, storedPrivateKey, temp, temp, temp, temp, temp, temp, temp = pickle.load(f)

		if myPublicKey is None:
			self.coss_client = PyCOSSClient(api_public=storedPublicKey, api_secret=storedPrivateKey)
		else:
			self.coss_client = PyCOSSClient(api_public=myPublicKey, api_secret=myPrivateKey)

	def checkConnection(self):
		connected = self.coss_client.test_connection()
		if connected:
			return True
		else:
			return False

	def getAllPairs(self, quotePair):
		pairList = []
		myExchangeInfo = self.coss_client.get_exchange_info()
		exchangeSymbols = myExchangeInfo["symbols"]
		symbolCount = 0
		for allSymbols in exchangeSymbols:
			actualQuotePair = exchangeSymbols[symbolCount]["symbol"].split('_')[1]
			if actualQuotePair == quotePair:
				pairList.append(exchangeSymbols[symbolCount]["symbol"].split('_')[0])
			symbolCount = symbolCount + 1

		return pairList

	def testKey(self):
		try:
			result = self.coss_client.get_balances()
		except:
			print("Failed to connect to exchange with provided API")
		if 'error' in result:
			return "Connected but failed to get data, API keys may be invalid"
		elif 'available' in result:
			return True

		return "Failed to Connect"


	def getCryptoBalance(self, quote = None, trade = None):
		try:
			result = self.coss_client.get_balances()
		except:
			print("Failed to connect")
			return "Failed to connect"

		if 'error' in result:
			print("API Error")
			return "Connected but Failed to get data, API keys may be invalid"
		else:
			#Get quote and trade pair balance
			returnBalances = {
				"quote": 0.0,
				"trade": 0.0
			}
			pairCount = 0
			for balances in result:
				if result[pairCount]['currency_code'] == quote:
					returnBalances["quote"] = result[pairCount]['available']
				elif result[pairCount]['currency_code'] == trade:
					returnBalances["trade"] = result[pairCount]['available']
				pairCount = pairCount + 1

			return returnBalances

	def getPairPrice(self, quote, trade):
		pair = trade + "_" + quote
		price = self.coss_client.get_market_price(pair)[0]["price"]
		return price

	def getPairAskBid(self, quote, trade):
		pair = trade + "_" + quote
		pairData = self.coss_client.get_order_book(pair)
		return [pairData['asks'][0][0], pairData['bids'][0][0]]


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
				quotesPair, tradePair, storedPublicKey, storedPrivateKey, orderSize, gridDistance, lowerPrice, higherPrice, numberOfGrids = pickle.load(f)

		if myPublicKey is None:
			print("Stored Public Key: " + storedPublicKey)
			print("Stored Private Key: " + storedPrivateKey)
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
			return False

		print(result)

		if 'error' in result:
			return False
		else:
			return True

	def getCryptoBalance(self, quote, trade):
		returnBalances = []

		#print(self.publicKey)
		#print(self.privateKey)

		
		allPairBalances = self.coss_client.get_balances()
		
		##print("Failed to get user balances")
		#return 0 

		print(allPairBalances)

		'''
		pairCount = 0
		print(allPairBalances)
		for balances in allPairBalances:
			if allPairBalances[pairCount]['currency_code'] == quote or allPairBalances[pairCount]['currency_code'] == trade:
				returnBalances.append(allPairBalances[pairCount]['available'])
			pairCount = pairCount + 1

		return returnBalances
		'''
		return "ended"
import pickle
from pycoss import PyCOSSClient
import tkinter as tk
import time
from tkinter import messagebox

publicKey = "Test"
privateKey = "Test2"

coss_client = PyCOSSClient(api_public=publicKey,
		                           api_secret=privateKey)


d = 0.0000001
strD = str(d)
myLength = len(strD)
print(strD)
print(myLength)

'''
orders = 0
with open('orderDb.pickle', 'rb') as handle:
	orders = pickle.load(handle)

count = 0
for myOrder in orders:
	print(myOrder)
	if myOrder['order_side'] == 'SELL':
		myOrder = {'empty': 'this order is empty'}
		orders[count] = myOrder
	time.sleep(1)
	count = count + 1

print(orders)
'''
#tk.messagebox.showinfo("Error creating buy order!", "Some error was encountered when creating a buy order, please ensure you have enough balance and you are above the minimum threshold for the trading pair.")
exit(0)

#Ensure connection to exchange is established
	#Save all settings to gridSettings.conf
with open('firstRun.txt', 'wb') as f:
	pickle.dump(0, f)

with open('gridSettings.conf', 'wb') as f:
	pickle.dump(["ETH", "COS", publicKey, privateKey, 0, 0, 0, 0, 0, 0, 0], f)

#get COSBalance
'''
pair = "ETH"
allPairBalances = coss_client.get_balances()
pairCount = 0
for balances in allPairBalances:
	if allPairBalances[pairCount]['currency_code'] == pair:
		print(allPairBalances[pairCount]['available'])
	pairCount = pairCount + 1
'''
	
#print(allPairBalances)
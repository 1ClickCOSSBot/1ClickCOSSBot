from pycoss import PyCOSSClient

publicKey = "Test"
privateKey = "Test"

coss_client = PyCOSSClient(api_public=publicKey,
		                           api_secret=privateKey)

#Ensure connection to exchange is established
connected = coss_client.test_connection()
if connected:
	print("Bot successfully connected to Exchange")
else:
	print("Some error occurred during connection")

#Check if user API keys are correct and can get their account balance

#Get list of all trading pairs available
exchangeInfo = coss_client.get_exchange_info()
print(len(exchangeInfo["symbols"]))

exchangeSymbols = exchangeInfo["symbols"]
symbolCount = 0
for allSymbols in exchangeSymbols:
	quotePair = exchangeSymbols[symbolCount]["symbol"].split('_')[1]
	if quotePair == "ETH":
		print(exchangeSymbols[symbolCount]["symbol"])
	symbolCount = symbolCount + 1

#Get lowest sell price
coss_ob = coss_client.get_order_book(symbol="COS_ETH")
print("Lowest sell price: " + coss_ob["asks"][1][0] + " Amount: " + coss_ob["asks"][0][1])

#Get highest bid price
print("Highest buy price: " + coss_ob["bids"][1][0] + " Amount: " + coss_ob["bids"][0][1])
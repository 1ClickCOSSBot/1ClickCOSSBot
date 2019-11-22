from pycoss import PyCOSSClient
import datetime
import time
import pickle

print("Hello World")

#Grab settings from gridSettings.conf

coss_client = PyCOSSClient(api_public="",
                           api_secret="")
coss_ob = coss_client.get_order_book(symbol="COS_ETH")
print(coss_ob["bids"][0])

#myName = "Omer"
#myFriend = "Ajay"
#todayDate = "Friday"

# Load Grid Settings: publicKey, privateKey, orderSize, gridDistance, lowerPrice, higherPrice, numberOfGrids
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
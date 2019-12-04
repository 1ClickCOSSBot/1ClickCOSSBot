import pickle
from pycoss import PyCOSSClient

publicKey = "Test"
privateKey = "Test"

coss_client = PyCOSSClient(api_public=publicKey,
		                           api_secret=privateKey)

#Ensure connection to exchange is established
	#Save all settings to gridSettings.conf
with open('firstRun.txt', 'wb') as f:
	pickle.dump(0, f)

with open('gridSettings.conf', 'wb') as f:
	pickle.dump(["ETH", "COS", "publicKey", "privateKey", 0, 0, 0, 0, 0], f)
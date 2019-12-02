from pycoss import PyCOSSClient

coss_client = PyCOSSClient(api_public=publicKey,
		                           api_secret=privateKey)

coss_ob = coss_client.get_order_book(symbol="COS_ETH")
print("Price: " + coss_ob["bids"][1][0] + " Amount: " + coss_ob["bids"][0][1])
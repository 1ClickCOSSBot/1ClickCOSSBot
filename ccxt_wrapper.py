import ccxt

print ('Starting CCXT Wrapper Test')

binance = ccxt.binance({
    'apiKey': '', # Your COSS Username
    'secret': 'aao1049c4af0bf657bdbm63018e84fc81bee786f6fa5dadff7f3e78ab836339da5br', # 
})

print("binance taker fees are: " + str(binance.fees["trading"]["taker"]))
print("binance maker fees are: " + str(binance.fees["trading"]["maker"]))

myMarkets = binance.fetch_tickers()
print(myMarkets["ETH/USDT"])

#myUSDT = binance.fetch_balance()
#print(myUSDT["USDT"]["free"])


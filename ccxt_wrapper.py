import ccxt

print ('Starting CCXT Wrapper Test')

class ccxtCOSSclient(object):

    def __init__(self, coss_username, coss_api_key):
        self.bytetrade = ccxt.bytetrade({
            'apiKey': coss_username, # Your COSS Username
            'secret': coss_api_key, # 
        })

    def get_exchange_status(self):
        exchange_status = self.bytetrade.fetch_status()
        return exchange_status['status']

    def get_all_exchange_pairs(self):
        markets = self.bytetrade.fetch_tickers()
        return markets

    def get_user_balance(self):
        balances = self.bytetrade.fetch_balance()
        return balances

my_name = ""
my_coss_key = "aao1049c4af0bf657bdbm63018e84fc81bee786f6fa5dadff7f3e78ab836339da5br"
my_client = ccxtCOSSclient(my_name, my_coss_key)
my_status = my_client.get_exchange_status()
print("Exchange status " + str(my_status))
import os, sys
import pickle
import threading, time
import requests
import tkinter as tk
import exchange
from exchange import exchangeInfo
import gridBot
from gridBot import gridBotStart
from os import path
from datetime import datetime 
from tkinter import *
from tkinter import messagebox
from PIL import Image, ImageTk
from functools import partial
from sys import exit

'''
Pre-Reqs
--------
Download and install python3 with pip
In a console or terminal run:
	pip install Pillow
	pip install requests
	(Linux only) sudo apt install python3-tk

Once all packages are installed please run this python script to start the UI
'''

#StaticVariables
CANVASHEIGHT=600
CANVASWIDTH=500
FRAMEHEIGHT=0.8
FRAMEWIDTH=0.8
FRAMEPADX=0.1
FRAMEPADY=0.125
BTNPADX_L=14
BTNPADX_S=10
BTNPADX_M=12
BTNPADY=5
HISTORYWIDTH=47
HISTORYHEIGHT=27.4

if os.name != "nt":
	CANVASHEIGHT=600
	CANVASWIDTH=700
	FRAMEHEIGHT=0.8
	FRAMEWIDTH=0.8
	FRAMEPADX=0.1
	FRAMEPADY=0.125
	BTNPADX_L=24
	BTNPADX_S=20
	BTNPADX_M=22
	BTNPADY=7
	HISTORYWIDTH=66
	HISTORYHEIGHT=25

#UI Colors
CANVASBG = "black"
BACKGROUND = CANVASBG
FOREGROUND = "white"
BTNBG = "grey"
BTNCLICKEDBG = "blue"
BTNFG = "black"
BTNCLICKEDFG = "white"
BTNFRAMEBG = CANVASBG

def initializeBot():
	#Load telegram settings
	if not os.path.exists("telegramSettings.conf"):
		with open('telegramSettings.conf', 'wb') as f:
			pickle.dump([False, "", ""], f)

	with open('telegramSettings.conf', 'rb') as f:
		isTelegramEnabled, getTelegramToken, getTelegramChatID = pickle.load(f)
	if isTelegramEnabled:
		enableTelegramChk.select()
		telegramCheckBoxChanged()
	tokenBox.delete(0, tk.END)
	tokenBox.insert(tk.END, getTelegramToken.strip())
	chatIDBox.delete(0, tk.END)
	chatIDBox.insert(tk.END, getTelegramChatID.strip())

	if isTelegramEnabled:
		sendTelegramMessage("An instance of your Simplicity COSS bot was just launched. If this wasn't you please login to your COSS account and disable your API keys immediately.", False)

#Clear all frames
def clearFrames():
	homeFrame.place_forget()
	settingsFrame.place_forget()
	runFrame.place_forget()
	aboutFrame.place_forget()
	historyFrame.place_forget()
	botOptionsFrame.place_forget()
	gridStratFrame.place_forget()
	blStratFrame.place_forget()

	homeBtn.config(bg=BTNBG, fg=BTNFG)
	runBtn.config(bg=BTNBG, fg=BTNFG)
	settingsBtn.config(bg=BTNBG, fg=BTNFG)
	aboutBtn.config(bg=BTNBG, fg=BTNFG)
	historyBtn.config(bg=BTNBG, fg=BTNFG)
	botOptionBtn.config(bg=BTNBG, fg=BTNFG)

#Create function for run button
def openHome():
	'''
	Switches frames to the home tab
	'''	
	clearFrames()
	homeBtn.config(bg=BTNCLICKEDBG, fg=BTNCLICKEDFG)
	homeFrame.place(relwidth=FRAMEHEIGHT, relheight=FRAMEWIDTH, relx=FRAMEPADX, rely=FRAMEPADY)

#Create function for settings/strategy button
def openSettings():
	'''
	Switches frames to the settings tab
	'''	
	clearFrames()
	settingsBtn.config(bg=BTNCLICKEDBG, fg=BTNCLICKEDFG)
	settingsFrame.place(relwidth=FRAMEHEIGHT, relheight=FRAMEWIDTH, relx=FRAMEPADX, rely=FRAMEPADY)
	gridStratFrame.place(relwidth=FRAMEWIDTH*0.9, relheight=FRAMEHEIGHT/1.8, relx=FRAMEPADX*1.4, rely=FRAMEPADY*3.1)

	#Load all grid strategy settings
	# Load Grid Settings
	with open('gridSettings.conf', 'rb') as f:  # Python 3: open(..., 'rb')
		quotesPair, tradePair, publicKey, privateKey, orderSize, gridDistance, lowerBuyPrice, higherBuyPrice, lowerSellPrice, higherSellPrice, numberGrids = pickle.load(f)
	quotePair.set(quotesPair)
	publicAPIKeyBox.delete(0, tk.END)
	publicAPIKeyBox.insert(tk.END, publicKey)
	privateAPIKeyBox.delete(0, tk.END)
	privateAPIKeyBox.insert(tk.END, privateKey)
	orderSizeBox.delete('1.0', tk.END)
	orderSizeBox.insert(tk.END, orderSize)
	gridDistanceBox.delete('1.0', tk.END)
	gridDistanceBox.insert(tk.END, gridDistance)
	#buyPriceLowerBox.delete('1.0', tk.END)
	#buyPriceLowerBox.insert(tk.END, lowerBuyPrice)
	#buyPriceHigherBox.delete('1.0', tk.END)
	#buyPriceHigherBox.insert(tk.END, higherBuyPrice)
	#sellPriceLowerBox.delete('1.0', tk.END)
	#sellPriceLowerBox.insert(tk.END, lowerSellPrice)
	#sellPriceHigherBox.delete('1.0', tk.END)
	#sellPriceHigherBox.insert(tk.END, higherSellPrice)
	numberOfGrids.set(numberGrids)
	quotePairChanged(None, tradePair)


#Create function for run button
def openRun():
	'''
	Switches frames to the run tab
	'''	
	#Load Strategy Settings
	with open('gridSettings.conf', 'rb') as f:  # Python 3: open(..., 'rb')
		quotePairRun, tradePairRun, publicAPIKey, privateAPIKey, orderSize, gridDistance, temp, temp, temp, temp, numberOfGrids = pickle.load(f)
		
	clearFrames()
	runBtn.config(bg=BTNCLICKEDBG, fg=BTNCLICKEDFG)

	#Check if API keys are correct
	loadPrice = exchangeInfo(publicAPIKey, privateAPIKey)

	#Get latest current price
	try: 
		latestPairPrice = loadPrice.getPairPrice(quotePairRun, tradePairRun)
	except:
		print("There was an error when fetching pair price")

	#Calculate start buy/sell and stop price ranges automatically
	if float(gridDistance) >= float(latestPairPrice):
		messagebox.showinfo("Warning", "Your grid distance cannot be greater than or equal to the current price of the pair! Please adjust your strategy")
		openSettings()
		return 0
	startBuyPrice = round(float(latestPairPrice) - float(gridDistance), 8)
	startSellPrice = round(float(latestPairPrice) + float(gridDistance), 8)
	stopBuyPrice = round((startBuyPrice - (float(gridDistance) * (float(numberOfGrids)/2))) - float(gridDistance), 9)
	stopSellPrice = round((startSellPrice + (float(gridDistance) * (float(numberOfGrids)/2))) + float(gridDistance), 9)

	#Update information in text fields
	runStrategyBox.config(state="normal")
	runStrategyBox.delete('1.0', tk.END)
	runStrategyBox.insert(tk.END, "Grid MM")
	runStrategyBox.config(state="disabled")
	runTradePairBox.config(state="normal")
	runTradePairBox.delete('1.0', tk.END)
	runTradePairBox.insert(tk.END, tradePairRun + "_" + quotePairRun)
	runTradePairBox.config(state="disabled")
	runInstanceNameBox.delete('1.0', tk.END)
	runInstanceNameBox.insert(tk.END, "Grid MM" + "_" + tradePairRun + "_" + quotePairRun)

	startBuyBox.delete('1.0', tk.END)
	startBuyBox.insert(tk.END, floatToStr(startBuyPrice))
	startSellBox.delete('1.0', tk.END)
	startSellBox.insert(tk.END, floatToStr(startSellPrice))
	stopBuyBox.delete('1.0', tk.END)
	stopBuyBox.insert(tk.END, floatToStr(stopBuyPrice))
	stopSellBox.delete('1.0', tk.END)
	stopSellBox.insert(tk.END, floatToStr(stopSellPrice))

	balancesRequired = calcRequiredBalance()

	quoteBalanceUseLabel.config(text=" Amount of " + quotePairRun + " needed for strategy:")
	tradeBalanceUseLabel.config(text=" Amount of " + tradePairRun + " needed for strategy:")
	quoteBalanceUseBox.config(state="normal")
	quoteBalanceUseBox.delete('1.0', tk.END)
	quoteBalanceUseBox.insert(tk.END, str(balancesRequired[0]))
	quoteBalanceUseBox.config(state="disabled")
	tradeBalanceUseBox.config(state="normal")
	tradeBalanceUseBox.delete('1.0', tk.END)
	tradeBalanceUseBox.insert(tk.END, str(balancesRequired[1]))
	tradeBalanceUseBox.config(state="disabled")

	runFrame.place(relwidth=FRAMEHEIGHT, relheight=FRAMEWIDTH, relx=FRAMEPADX, rely=FRAMEPADY)

#Create function for about button
def openAbout():
	'''
	Switches frames to the about tab
	'''	
	clearFrames()
	aboutBtn.config(bg=BTNCLICKEDBG, fg=BTNCLICKEDFG)
	aboutFrame.place(relwidth=FRAMEHEIGHT, relheight=FRAMEWIDTH, relx=FRAMEPADX, rely=FRAMEPADY)

#Create function for history button
def openHistory():
	'''
	Switches frames to the about tab
	'''	
	clearFrames()
	historyBtn.config(bg=BTNCLICKEDBG, fg=BTNCLICKEDFG)
	historyFrame.place(relwidth=FRAMEHEIGHT, relheight=FRAMEWIDTH, relx=FRAMEPADX, rely=FRAMEPADY)

#Create function for botOptions button
def openOptions():
	'''
	Switches frames to the options setting tab
	'''
	clearFrames()

	botOptionBtn.config(bg=BTNCLICKEDBG, fg=BTNCLICKEDFG)
	botOptionsFrame.place(relwidth=FRAMEHEIGHT, relheight=FRAMEWIDTH, relx=FRAMEPADX, rely=FRAMEPADY)

def historyReresh():
	while True:
		if os.path.exists("history.txt"):
			with open("history.txt", "rb") as f2:
				f2.seek(0)
				historyTextField.delete("1.0", tk.END)
				historyTextField.insert(tk.END, f2.read())
				historyTextField.see("end")
		time.sleep(10)

def tradingPairChanged(event, pair):
	'''
	Update settings page with new trading pair
	'''
	if pair is not None:
		tradingPair.set(pair)
	tradePairBalanceLabel.config(text="    Trade Balance (" + tradingPair.get() + ")")
	orderSizeLabel.config(text="    Order Size (" + tradingPair.get() + ")")

	#Load selected pair balances
	balances = {
		"quote": 0.0,
		"trade": 0.0
	}
	balancePublicKey = publicAPIKeyBox.get().strip()
	balancePrivateKey = privateAPIKeyBox.get().strip()
	balanceKeys = exchangeInfo(balancePublicKey, balancePrivateKey)
	try:
		balances = balanceKeys.getCryptoBalance(quotePair.get(), tradingPair.get())
	except:
		print("There was some error when loading balances")

	if "quote" in balances:
		quotePairBalanceBox.config(state="normal")
		quotePairBalanceBox.delete('1.0', tk.END)
		quotePairBalanceBox.insert(tk.END, balances["quote"])
		quotePairBalanceBox.config(state="disabled")
		tradePairBalanceBox.config(state="normal")
		tradePairBalanceBox.delete('1.0', tk.END)
		tradePairBalanceBox.insert(tk.END, balances["trade"])
		tradePairBalanceBox.config(state="disabled")
	else:
		print("Cannot access balances due to API error")
		quotePairBalanceBox.config(state="normal")
		quotePairBalanceBox.delete('1.0', tk.END)
		quotePairBalanceBox.insert(tk.END, "N/A")
		quotePairBalanceBox.config(state="disabled")
		tradePairBalanceBox.config(state="normal")
		tradePairBalanceBox.delete('1.0', tk.END)
		tradePairBalanceBox.insert(tk.END, "N/A")
		tradePairBalanceBox.config(state="disabled")

	pairPrice = 0
	try: 
		pairPrice = balanceKeys.getPairPrice(quotePair.get(), tradingPair.get())
	except:
		print("There was an error when fetching pair price")
	currentPriceBox.config(state="normal")
	currentPriceBox.delete('1.0', tk.END)
	currentPriceBox.insert(tk.END, pairPrice)
	currentPriceBox.config(state="disabled")

def quotePairChanged(event, trade = None):

	#Update trading pair options
	allPairs = myExchange.getAllPairs(str(quotePair.get()))
	allPairs.sort()
	tradingPair.set(allPairs[0])
	pairMenu['menu'].delete(0, 'end')

    # Insert list of new options (tk._setit hooks them up to var)
	new_choices = allPairs
	tradingEventWithArgs = partial(tradingPairChanged, None)
	for choice in new_choices:
		pairMenu['menu'].add_command(label=choice, command=partial(tradingPairChanged, None, choice))
	tradingPairChanged(None, trade)

	quotePairBalanceLabel.config(text="    Quote Balance (" + quotePair.get() + ")")
	#buyRangeLabel.config(text="    Stop Price Range (" + quotePair.get() + ")")
	#sellRangeLabel.config(text="    Start Buy / Sell (" + quotePair.get() + ")")
	gridDistanceLabel.config(text="    Grid Distance (" + quotePair.get() + ")")
	currentPriceLabel.config(text="    Current Price (" + quotePair.get() + ")")

def stratMenuChanged(event):
	'''
	Update settings UI to reflect changed strategy
	'''
	if tradingStrat.get() == "Buy Low Sell High":
		tradingStrat.set(tradingStratOptions[0])
		messagebox.showinfo("Alert", "This strategy is not yet supported")
	elif tradingStrat.get() == "GRID MM":
		blStratFrame.place_forget()
		gridStratFrame.place(relwidth=FRAMEWIDTH*0.9, relheight=FRAMEHEIGHT/1.9, relx=FRAMEPADX*1.4, rely=FRAMEPADY*3.1)
	#print("Strategy was changed to " + tradingStrat.get())

def saveStrategy():
	#Check if API keys are correct
	testPublicKey = publicAPIKeyBox.get().strip()
	testPrivateKey = privateAPIKeyBox.get().strip()
	testKeys = exchangeInfo(testPublicKey, testPrivateKey)
	testConnection = testKeys.testKey()
	if testConnection:
		messagebox.showinfo("Saved", "Your strategy settings will be applied")
		myExchange = testKeys
	else:
		messagebox.showinfo("Invalid", "Looks like you entered invalid API keys. Please try again!")
		return 0

	#Save all settings to gridSettings.conf
	with open('gridSettings.conf', 'wb') as f:
		pickle.dump([quotePair.get().strip(), tradingPair.get().strip(), testPublicKey, testPrivateKey, orderSizeBox.get("1.0", tk.END).strip(), gridDistanceBox.get("1.0", tk.END).strip(), 0, 0, 0, 0, numberOfGrids.get()], f)
	openRun()
	return 1

def floatToStr(originalNumber):
	actualNumber = float(originalNumber)
	decimalCount = 0
	while actualNumber < 1:
		actualNumber = actualNumber * 10
		decimalCount = decimalCount + 1

	if float(originalNumber) <= 1:
		myString = "0."
		for i in range(decimalCount-1):
			myString = myString + "0" 
		myString = myString + str(int(float(originalNumber) * (10**(decimalCount+3))))
	else:
		myString = str(actualNumber)
	return myString

def startStrategy():

	#Load saved settings and append prices then save
	with open('gridSettings.conf', 'rb') as f:
		quotePair, tradePair, publicKey, privateKey, orderSize, gridDistance, temp, temp, temp, temp, numberOfGrids = pickle.load(f)

	with open('gridSettings.conf', 'wb') as f:
		pickle.dump([quotePair, tradePair, publicKey, privateKey, orderSize, gridDistance, stopBuyBox.get("1.0", tk.END), startBuyBox.get("1.0", tk.END), startSellBox.get("1.0", tk.END), stopSellBox.get("1.0", tk.END), numberOfGrids], f)
	
	strategyWithArg = partial(strategyThread, runInstanceNameBox.get("1.0", tk.END).replace(" ", ""))
	strategyTestThread = threading.Thread(target=strategyWithArg)
	strategyTestThread.daemon = True
	strategyTestThread.start()

	openHistory()

def strategyThread(name):
	myGridBot = gridBotStart
	myGridBot.gridStart(name)

def autoStrategy():
	#Build Strategy settings automatically for user
	pairPrice = 0
	userQuoteBalance = 0
	userTradeBalance = 0
	useMaxBalance = tk.messagebox.askquestion('Warning','When using the auto strategy option Simplicity uses your maximum balances available. Once the strategy is autoconfigured you can simply reduce balance used by lowering the ordersize or reducing number of grids. Would you like to continue?')

	if useMaxBalance == "no":
		return 0	

	messagebox.showinfo("Alert", "Simplicity will now gather some data. This may take a few seconds.")

	#Get pair data from exchange
	#Load selected pair balances
	balances = {
		"quote": 0.0,
		"trade": 0.0
	}
	balancePublicKey = publicAPIKeyBox.get().strip()
	balancePrivateKey = privateAPIKeyBox.get().strip()
	balanceKeys = exchangeInfo(balancePublicKey, balancePrivateKey)
	try:
		balances = balanceKeys.getCryptoBalance(quotePair.get(), tradingPair.get())
	except:
		print("There was some error when loading balances")
		messagebox.showinfo("Error", "There was some error when loading balances. Strategy could not be automatically configured")
		return 0
	userQuoteBalance = float(balances[0])
	userTradeBalance = float(balances[1])

	try: 
		pairPrice = balanceKeys.getPairPrice(quotePair.get(), tradingPair.get())
	except:
		print("There was an error when fetching pair price")
		messagebox.showinfo("Error", "There was an error when fetching pair price. Strategy could not be automatically configured")
		return 0

	calcOrderSize = 0
	calcGridDistance = 0
	calcStartBuy = 0
	calcStartSell = 0
	calcLowPrice = 0
	calcHighPrice = 0
	calcGrids = 0

def calcRequiredBalance():
	balancesRequired = [0, 0]

	#Load Strategy Settings
	with open('gridSettings.conf', 'rb') as f:  # Python 3: open(..., 'rb')
		quoteCalc, tradeCalc, temp, temp, orderSize, gridDistance, temp, temp, temp, temp, numberOfGrids = pickle.load(f)

	oneSideGrids = int(numberOfGrids)/2
	buyStartPrice = float(startBuyBox.get("1.0", tk.END))
	sellStartPrice = float(startSellBox.get("1.0", tk.END))

	#Calculate quote balance required
	total = 0
	currentPrice = float(buyStartPrice)
	if numberOfGrids > 3:
		for x in range(int(oneSideGrids)):
			total = total + (float(orderSize) * float(currentPrice))
			currentPrice = currentPrice - float(gridDistance)
		total = round(total, 8)
	else:
		total = round(float(orderSize) * float(currentPrice), 8)
	balancesRequired[0] = total

	#Calculate trade balance required
	tradeBalance = float(float(orderSize) * int(oneSideGrids))
	balancesRequired[1] = tradeBalance
	#Return balances
	return balancesRequired

def cancelAllOrders():
	cancelAnswer = tk.messagebox.askquestion('Stop strategy?','Are you sure you want to stop the strategy and cancel all your orders? (Note: If you just want to restart the bot and not cancel orders, click no on this message and just close the window and re-start the bot from the run page)')
	if cancelAnswer == 'yes':
		print("Attempting to cancel all orders")
		cancelBot = gridBotStart
		cancelBot.cancelAndExit()
		print("Bot will exit in 5 seconds! You can restart the bot to re-run the strategy.")
		time.sleep(5)
		exit(0)

def telegramCheckBoxChanged():
	if telegramVar.get() == 0:
		confirmDisableTelegram = messagebox.askquestion('Disable Telegram', 'Are you sure you want to disable telegram alerts?')
		if confirmDisableTelegram == 'no':
			enableTelegramChk.select()
			return 0
		with open('telegramSettings.conf', 'wb') as f:
			pickle.dump([False, tokenBox.get().strip(), chatIDBox.get().strip()], f)
		testTelegramBtn.config(state="disabled")
		tokenBox.config(state="disabled")
		chatIDBox.config(state="disabled")
	else:
		testTelegramBtn.config(state="normal")
		tokenBox.config(state="normal")
		chatIDBox.config(state="normal")

		with open('telegramSettings.conf', 'rb') as f:  # Python 3: open(..., 'rb')
			temp, getTelegramTokenChange, getTelegramChatIDChange = pickle.load(f)

		tokenBox.delete(0, tk.END)
		tokenBox.insert(tk.END, getTelegramTokenChange.strip())
		chatIDBox.delete(0, tk.END)
		chatIDBox.insert(tk.END, getTelegramChatIDChange.strip())
		#messagebox.showinfo("Telegram Enabled", "To enable telegram alerts please insert your Telegram bot token and chat ID then press the 'Test and Save' button to enable.")

def sendTelegramMessage(message, isATest):
	'''
	Send a Telegram message to users telegram bot
	'''
	if isATest:
		telegramToken = tokenBox.get().strip()
		telegramChatID = chatIDBox.get().strip()
		messagebox.showinfo("Telegram Test", "The bot will now send a message to your telegram bot and save your telegram settings. If you don't recieve it please confirm your token and chat ID are correct and try again.")
		messageSender = 'https://api.telegram.org/bot' + telegramToken + '/sendMessage?chat_id=' + telegramChatID + '&parse_mode=Markdown&text=' + message
		#Save all settings to gridSettings.conf
		with open('telegramSettings.conf', 'wb') as f:
			pickle.dump([isATest, telegramToken, telegramChatID], f)

	else:
		telegramToken = tokenBox.get()
		telegramChatID = chatIDBox.get()
		messageSender = 'https://api.telegram.org/bot' + telegramToken + '/sendMessage?chat_id=' + telegramChatID + '&parse_mode=Markdown&text=' + message

	response = requests.get(messageSender)
	return response.json()

#Create an instance of exchange object and check connection
myExchange = exchangeInfo()

#Create the root UI
root = tk.Tk()
#root.configure(bg='#282923')
root.resizable(False, False)
if os.name == "nt":
	root.attributes('-alpha', 0.97)

#Define Main UI elements
canvas = tk.Canvas(root, height=CANVASHEIGHT, width=CANVASWIDTH, bg=CANVASBG)
btnFrame = tk.Frame(root, bg=BTNFRAMEBG)
homeFrame = tk.Frame(root, bg=BACKGROUND)
runFrame = tk.Frame(root, bg=BACKGROUND)
settingsFrame = tk.Frame(root, bg=BACKGROUND)
aboutFrame = tk.Frame(root,bg=BACKGROUND)
historyFrame = tk.Frame(root,bg=BACKGROUND)
notificationFrame = tk.Frame(root, bg=BACKGROUND)
botOptionsFrame = tk.Frame(root, bg=BACKGROUND)
homeBtn = tk.Button(root, text="Home", padx=BTNPADX_S, pady=5, highlightbackground=BTNFRAMEBG, fg=BTNCLICKEDFG, bg=BTNCLICKEDBG, height=1, width=4, command=openHome, relief=FLAT)
runBtn = tk.Button(root, text="Run", padx=BTNPADX_S, pady=5, highlightbackground=BTNFRAMEBG, fg=BTNFG, bg=BTNBG, height=1, width=4, command=openRun, relief=FLAT)
settingsBtn = tk.Button(root, text="Strategy", padx=BTNPADX_S, pady=5, highlightbackground=BTNFRAMEBG, fg=BTNFG, bg=BTNBG, height=1, width=4, command=openSettings, relief=FLAT)
historyBtn = tk.Button(root, text="History", padx=BTNPADX_S, pady=5, highlightbackground=BTNFRAMEBG, fg=BTNFG, bg=BTNBG, height=1, width=4, command=openHistory, relief=FLAT)
botOptionBtn = tk.Button(root, text="Settings", padx=BTNPADX_M, pady=5, highlightbackground=BTNFRAMEBG, fg=BTNFG, bg=BTNBG, height=1, width=4, command=openOptions, relief=FLAT)
aboutBtn = tk.Button(root, text="About", padx=BTNPADX_S, pady=5, highlightbackground=BTNFRAMEBG, fg=BTNFG, bg=BTNBG, height=1, width=4, command=openAbout, relief=FLAT)
exchangeBtn = tk.Button(root, text="Extras", padx=BTNPADX_L, pady=5, highlightbackground=BTNFRAMEBG, fg="white", bg="#663399", height=1, width=4, command=openAbout, relief=FLAT)

#Define Home page UI elements
homeInfo = tk.Text(homeFrame, relief=FLAT, fg=FOREGROUND, bg=BACKGROUND, height=24, width=47)
homeInfo.pack()
homeInfo.insert(tk.END, "\nSimplicity COSS Bot - Version 1.0\n\nTo get started please first customize your bot\nfrom the strategy tab. You can also enable\ntelegram messaging from the settings tab.")
homeInfo.insert(tk.END, "\n\nOnce configured you can run the bot from the\nrun tab")
homeInfo.insert(tk.END, "\n\nLatest Updates (1/5/2020)\n---------------------------\n - New simplified strategy UI!\n - Added auto calculation of start/sell prices\n - Added auto calculation of stop prices\n - Optional price adjustments on run page\n - Changed default starting pair\n - Code cleanup and bug fixes")
homeInfo.insert(tk.END, "\n\nTrading is very risky, the use of this tool may\nresult in significant losses")
homeInfo.insert(tk.END, "\n\nTo protect your primary COSS account, always\ncreate a second account for use with public\ntrading bots.")
homeInfo.config(state="disabled")

if os.name == "nt":
	cossPhoto = ImageTk.PhotoImage(Image.open("coss2.png"))
	cossPhotoLabel = tk.Label(homeFrame,text="image",image=cossPhoto, bg=BACKGROUND)
	cossPhotoLabel.pack()
else:
	print("Images not supported in this OS") 

#Define Settings page UI elements
tk.Label(settingsFrame, text="", bg=BACKGROUND).grid(row=0)

publicLabel = tk.Label(settingsFrame, text="   Public API Key")
publicLabel.config(relief=FLAT, bg=BACKGROUND, fg=FOREGROUND)
publicLabel.grid(row=1, sticky="W")
publicAPIKeyBox = tk.Entry(settingsFrame, show="*", width=46)
publicAPIKeyBox.grid(row=1, column=1)

privateLabel = tk.Label(settingsFrame, text="   Private API Key")
privateLabel.config(relief=FLAT, bg=BACKGROUND, fg=FOREGROUND)
privateLabel.grid(row=2, sticky="W")
privateAPIKeyBox = tk.Entry(settingsFrame, show="*", width=46)
privateAPIKeyBox.grid(row=2, column=1)

#tk.Label(settingsFrame, text="", bg=BACKGROUND).grid(row=3)
tradingPairText = tk.Label(settingsFrame, text="   Quote Pair")
tradingPairText.config(relief=FLAT, bg=BACKGROUND, fg=FOREGROUND)
tradingPairText.grid(row=3, column=0, sticky="W")
quotePairOptions = [
    "ETH",
    "BTC",
    "COS",
    "USDT",
    "DAI",
    "USD",
    "EUR"
]
quotePair = StringVar(settingsFrame)
quotePair.set(quotePairOptions[0])
quoteMenu = OptionMenu(*(settingsFrame, quotePair) + tuple(quotePairOptions), command=quotePairChanged)
quoteMenu.config(bg=BACKGROUND, fg=FOREGROUND, relief=FLAT)
quoteMenu["menu"].config(bg=BACKGROUND, fg=FOREGROUND, relief=FLAT)
quoteMenu["highlightthickness"]=0
quoteMenu.grid(row=3, column=1)

tradingPairText = tk.Label(settingsFrame, text="   Trade Pair")
tradingPairText.config(relief=FLAT, bg=BACKGROUND, fg=FOREGROUND)
tradingPairText.grid(row=4, column=0, sticky="W")
tradingPairOptions = [
	"Temp",
	"Temp2"
]
tradingPair = StringVar(settingsFrame)
tradingPair.set("temp") # initial value
pairMenu = OptionMenu(*(settingsFrame, tradingPair) + tuple(tradingPairOptions), command=tradingPairChanged)
pairMenu.config(bg=BACKGROUND, fg=FOREGROUND, relief=FLAT)
pairMenu["menu"].config(bg=BACKGROUND, fg=FOREGROUND, relief=FLAT)
pairMenu["highlightthickness"]=0
pairMenu.grid(row=4, column=1)

tradingStratText = tk.Label(settingsFrame, text="   Trading Strategy")
tradingStratText.config(relief=FLAT, bg=BACKGROUND, fg=FOREGROUND)
tradingStratText.grid(row=5, column=0, sticky="W")
tradingStratOptions = [
    "GRID MM",
    "Buy Low Sell High"
]
tradingStrat = StringVar(settingsFrame)
tradingStrat.set(tradingStratOptions[0]) # initial value
stratMenu = OptionMenu(*(settingsFrame, tradingStrat) + tuple(tradingStratOptions), command=stratMenuChanged)
stratMenu.config(bg=BACKGROUND, fg=FOREGROUND, relief=FLAT)
stratMenu["menu"].config(bg=BACKGROUND, fg=FOREGROUND, relief=FLAT)
stratMenu["highlightthickness"]=0
stratMenu.grid(row=5, column=1)

#Define bottom frame for Settings page apply button
saveStratFrame = tk.Frame(settingsFrame, bg=BACKGROUND)
saveStratFrame.place(relwidth=FRAMEWIDTH*1.25, relheight=FRAMEHEIGHT/6.5, relx=0, rely=FRAMEPADY*7.2)
saveBtn = tk.Button(saveStratFrame, text="Save", padx=10, pady=5, highlightbackground=BACKGROUND, fg=BTNFG, bg=BTNBG, height=1, width=4, command=saveStrategy, relief=FLAT)
saveBtn.pack()
#tk.Label(saveStratFrame, text="This strategy is not yet implemented", bg="#482923", fg=FOREGROUND).pack()

#Define UI elements for Buy Low Sell High Strategy Frame
blStratFrame = tk.Frame(root, bg="#482923")
tk.Label(blStratFrame, text="This strategy is not yet implemented", bg="#482923", fg=FOREGROUND).pack()

#Define UI elements for GRID Strategy Frame
gridStratFrame = tk.Frame(root, bg="#182923")

tk.Label(gridStratFrame, text="                         ", bg="#182923").grid(row=0, column=1)

currentPriceLabel = tk.Label(gridStratFrame, text="    Current Price (" + quotePair.get() + ")")
currentPriceLabel.config(relief=FLAT, bg="#182923", fg=FOREGROUND)
currentPriceLabel.grid(row=1, column=0, sticky="W")
currentPriceBox = tk.Text(gridStratFrame, width=12, height=1)
currentPriceBox.insert(tk.END, "2.67")
currentPriceBox.config(state="disabled", bg="#182923", fg=FOREGROUND)
currentPriceBox.grid(row=1, column=2)

tk.Label(gridStratFrame, text="                         ", bg="#182923").grid(row=2, column=1)
tk.Label(gridStratFrame, text="Available Balances", bg="#182923", fg=FOREGROUND, font='Helvetica 8 bold').grid(row=3, column=1)

tradePairBalanceLabel = tk.Label(gridStratFrame, text="    Trade Balance (" + tradingPair.get() + ")")
tradePairBalanceLabel.config(relief=FLAT, bg="#182923", fg=FOREGROUND)
tradePairBalanceLabel.grid(row=4, column=0, sticky="W")
tradePairBalanceBox = tk.Text(gridStratFrame, width=12, height=1)
tradePairBalanceBox.insert(tk.END, "30000")
tradePairBalanceBox.config(state="disabled", bg="#182923", fg=FOREGROUND)
tradePairBalanceBox.grid(row=4, column=2)

quotePairBalanceLabel = tk.Label(gridStratFrame, text="    Quote Balance (" + quotePair.get() + ")")
quotePairBalanceLabel.config(relief=FLAT, bg="#182923", fg=FOREGROUND)
quotePairBalanceLabel.grid(row=5, column=0, sticky="W")
quotePairBalanceBox = tk.Text(gridStratFrame, width=12, height=1)
quotePairBalanceBox.insert(tk.END, "2.67")
quotePairBalanceBox.config(state="disabled", bg="#182923", fg=FOREGROUND)
quotePairBalanceBox.grid(row=5, column=2)

tk.Label(gridStratFrame, text="                         ", bg="#182923").grid(row=6, column=1)
tk.Label(gridStratFrame, text="Grid Settings", bg="#182923", fg=FOREGROUND, font='Helvetica 8 bold').grid(row=7, column=1)

orderSizeLabel = tk.Label(gridStratFrame, text="    Order Size (" + tradingPair.get() + ")")
orderSizeLabel.config(relief=FLAT, bg="#182923", fg=FOREGROUND)
orderSizeLabel.grid(row=8, column=0, sticky="W")
orderSizeBox = tk.Text(gridStratFrame, width=12, height=1)
orderSizeBox.insert(tk.END, "0.015")
orderSizeBox.config(bg="white", fg="black")
orderSizeBox.grid(row=8, column=2)

gridDistanceLabel = tk.Label(gridStratFrame, text="    Grid Distance (" + quotePair.get() + ")")
gridDistanceLabel.config(relief=FLAT, bg="#182923", fg=FOREGROUND)
gridDistanceLabel.grid(row=9, column=0, sticky="W")
gridDistanceBox = tk.Text(gridStratFrame, width=12, height=1)
gridDistanceBox.insert(tk.END, "0.000001")
gridDistanceBox.config(bg="white", fg="black")
gridDistanceBox.grid(row=9, column=2)

gridNumberLabel = tk.Label(gridStratFrame, text="\n    Number Of Grids")
gridNumberLabel.config(relief=FLAT, bg="#182923", fg=FOREGROUND)
gridNumberLabel.grid(row=10, column=0, sticky="W")
numberOfGrids = Scale(gridStratFrame, from_=2, to=500, resolution=2, orient=HORIZONTAL, bg="#182923", fg=FOREGROUND, relief=FLAT, length=210)
numberOfGrids["highlightthickness"]=0
numberOfGrids.grid(row=10, column=1, columnspan=2)

#Define Run page UI elements
tk.Label(runFrame, text="", bg=BACKGROUND).grid(row=0, column=1)

runStrategyLabel = tk.Label(runFrame, text=" Selected Trading Strategy:")
runStrategyLabel.config(relief=FLAT, bg=BACKGROUND, fg=FOREGROUND)
runStrategyLabel.grid(row=1, column=0, sticky="W")
runStrategyBox = tk.Text(runFrame, width=12, height=1)
runStrategyBox.config(state="disabled", bg=BACKGROUND, fg=FOREGROUND)
runStrategyBox.grid(row=1, column=2, sticky="W")

runTradePairLabel = tk.Label(runFrame, text=" Selected Trading Pair:")
runTradePairLabel.config(relief=FLAT, bg=BACKGROUND, fg=FOREGROUND)
runTradePairLabel.grid(row=2, column=0, sticky="W")
runTradePairBox = tk.Text(runFrame, width=12, height=1)
runTradePairBox.config(state="disabled", bg=BACKGROUND, fg=FOREGROUND)
runTradePairBox.grid(row=2, column=2, sticky="W")

quoteBalanceUseLabel = tk.Label(runFrame, text=" Amount of " + quotePair.get() + " needed:")
quoteBalanceUseLabel.config(relief=FLAT, bg=BACKGROUND, fg=FOREGROUND)
quoteBalanceUseLabel.grid(row=3, column=0, sticky="W")
quoteBalanceUseBox = tk.Text(runFrame, width=12, height=1)
quoteBalanceUseBox.config(state="disabled", bg=BACKGROUND, fg=FOREGROUND)
quoteBalanceUseBox.grid(row=3, column=2, sticky="W")

tradeBalanceUseLabel = tk.Label(runFrame, text=" Amount of " + tradingPair.get() + " needed:")
tradeBalanceUseLabel.config(relief=FLAT, bg=BACKGROUND, fg=FOREGROUND)
tradeBalanceUseLabel.grid(row=4, column=0, sticky="W")
tradeBalanceUseBox = tk.Text(runFrame, width=12, height=1)
tradeBalanceUseBox.config(state="disabled", bg=BACKGROUND, fg=FOREGROUND)
tradeBalanceUseBox.grid(row=4, column=2, sticky="W")

startBuyLabel = tk.Label(runFrame, text=" Starting Buy Price (" + quotePair.get() + ")")
startBuyLabel.config(relief=FLAT, bg=BACKGROUND, fg=FOREGROUND)
startBuyLabel.grid(row=5, column=0, sticky="W")
startBuyBox = tk.Text(runFrame, width=12, height=1)
startBuyBox.insert(tk.END, "1")
startBuyBox.config(bg="white", fg="black")
startBuyBox.grid(row=5, column=2, sticky="W")

startSellLabel = tk.Label(runFrame, text=" Starting Sell Price (" + quotePair.get() + ")")
startSellLabel.config(relief=FLAT, bg=BACKGROUND, fg=FOREGROUND)
startSellLabel.grid(row=6, column=0, sticky="W")
startSellBox = tk.Text(runFrame, width=12, height=1)
startSellBox.insert(tk.END, "1")
startSellBox.config(bg="white", fg="black")
startSellBox.grid(row=6, column=2, sticky="W")

stopBuyLabel = tk.Label(runFrame, text=" Lowest Buy Price (" + quotePair.get() + ")")
stopBuyLabel.config(relief=FLAT, bg=BACKGROUND, fg=FOREGROUND)
stopBuyLabel.grid(row=7, column=0, sticky="W")
stopBuyBox = tk.Text(runFrame, width=12, height=1)
stopBuyBox.insert(tk.END, "1")
stopBuyBox.config(bg="white", fg="black")
stopBuyBox.grid(row=7, column=2, sticky="W")

stopSellLabel = tk.Label(runFrame, text=" Highest Sell Price (" + quotePair.get() + ")")
stopSellLabel.config(relief=FLAT, bg=BACKGROUND, fg=FOREGROUND)
stopSellLabel.grid(row=8, column=0, sticky="W")
stopSellBox = tk.Text(runFrame, width=12, height=1)
stopSellBox.insert(tk.END, "1")
stopSellBox.config(bg="white", fg="black")
stopSellBox.grid(row=8, column=2, sticky="W")

runInstanceNameLabel = tk.Label(runFrame, text=" Name of Bot Instance:")
runInstanceNameLabel.config(relief=FLAT, bg=BACKGROUND, fg=FOREGROUND)
runInstanceNameLabel.grid(row=9, column=0, sticky="W")
runInstanceNameBox = tk.Text(runFrame, width=20, height=1)
runInstanceNameBox.config(state="normal", bg="white", fg="black")
runInstanceNameBox.grid(row=9, column=2, columnspan=2)

#Define bottom frame for run page start button
startRunFrame = tk.Frame(runFrame, bg=BACKGROUND)
startRunFrame.place(relwidth=FRAMEWIDTH*1.25, relheight=FRAMEHEIGHT/6.5, relx=0, rely=FRAMEPADY*7.2)
startBtn = tk.Button(startRunFrame, text="Start", padx=10, pady=5, highlightbackground=BACKGROUND, fg=BTNFG, bg=BTNBG, height=1, width=4, command=startStrategy, relief=FLAT)
startBtn.pack()

#Define Options page UI elements
tk.Label(botOptionsFrame, text="       ", bg=BACKGROUND).grid(row=0, column=1)

telegramVar = tk.IntVar()
enableTelegramChk = tk.Checkbutton(botOptionsFrame, text="Telegram", variable=telegramVar, command=telegramCheckBoxChanged)
enableTelegramChk.config(bg=BACKGROUND, fg="red")
enableTelegramChk.grid(row=1, sticky="W")

testMessage_withArg = partial(sendTelegramMessage, "This is a test!", True)
testTelegramBtn = tk.Button(botOptionsFrame, text="Test and Save", padx=35, highlightbackground=BTNFRAMEBG, fg="white", bg="#082923", height=1, width=4, command=testMessage_withArg, relief=FLAT)
testTelegramBtn.grid(row=1, column=2)

tokenLabel = tk.Label(botOptionsFrame, text=" Bot Token")
tokenLabel.config(relief=FLAT, bg=BACKGROUND, fg=FOREGROUND)
tokenLabel.grid(row=2, sticky="W")
tokenBox = tk.Entry(botOptionsFrame, width=46)
tokenBox.grid(row=2, column=2)

chatIDLabel = tk.Label(botOptionsFrame, text=" Bot Chat ID")
chatIDLabel.config(relief=FLAT, bg=BACKGROUND, fg=FOREGROUND)
chatIDLabel.grid(row=3, sticky="W")
chatIDBox = tk.Entry(botOptionsFrame, width=46)
chatIDBox.grid(row=3, column=2)

#Define About page UI elements
aboutInfo = tk.Text(aboutFrame, relief=FLAT, fg=FOREGROUND, bg=BACKGROUND, height=24, width=47)
aboutInfo.pack()
aboutInfo.insert(tk.END, "\nBot created by Omer \nTelegram: @omer259\nReddit: https://www.reddit.com/user/Omer259/")
aboutInfo.insert(tk.END, "\n\nBitcoin Donation Address: \nbc1qnjcnhcex50659vxnuhdkuzhhu4m0ewmx6p43j2")
aboutInfo.insert(tk.END, "\n\nEthereum Donation Address: \n0xE9b79A87520DFB16824d9AfC40a7d8bC1a81a753")
aboutInfo.insert(tk.END, "\n\nAll trading performed using this bot is\nat your own risk. I will not be held\nresponsible for any gains or losses caused by\nthe use of this tool")
aboutInfo.config(state="disabled")

#Define History page UI elements
scroll = Scrollbar(historyFrame)
scroll.grid(row=1, column=2, sticky="W", ipady=191.70)
tk.Label(historyFrame, text="", bg=BACKGROUND).grid(row=0, column=0)
historyTextField = tk.Text(historyFrame, bg=BACKGROUND, fg=FOREGROUND, yscrollcommand=scroll.set, width=HISTORYWIDTH, height=HISTORYHEIGHT)
historyTextField.grid(row=1, column=1, sticky="W")
scroll.config(command=historyTextField.yview)

#Define bottom frame for run page start button
cancelOrderFrame = tk.Frame(historyFrame, bg=BACKGROUND)
cancelOrderFrame.place(relwidth=FRAMEWIDTH*1.25, relheight=FRAMEHEIGHT/6.5, relx=0, rely=FRAMEPADY*7.2)
cancelOrderBtn = tk.Button(cancelOrderFrame, text="Cancel Orders and Stop", padx=10, pady=4, highlightbackground=BACKGROUND, fg=BTNFG, bg=BTNBG, height=1, width=18, command=cancelAllOrders, relief=FLAT)
cancelOrderBtn.pack()

#Setup UI elements
root.winfo_toplevel().title("Simplicity")

if os.name == "nt":
	root.iconbitmap('coss.ico')
else:
	print("Icons not supported in this OS")

canvas.pack()
btnFrame.place(relwidth=0.8, relheight=0.05, relx=0.1, rely=0.075)
homeFrame.place(relwidth=FRAMEWIDTH, relheight=FRAMEHEIGHT, relx=FRAMEPADX, rely=FRAMEPADY)
homeBtn.pack(in_=btnFrame, side=LEFT)
homeBtn.config(bg=BTNCLICKEDBG)
runBtn.pack(in_=btnFrame, side=LEFT)
settingsBtn.pack(in_=btnFrame, side=LEFT)
historyBtn.pack(in_=btnFrame, side=LEFT)
botOptionBtn.pack(in_=btnFrame, side=LEFT)
aboutBtn.pack(in_=btnFrame, side=LEFT)
exchangeBtn.config(state="disabled")
exchangeBtn.pack(in_=btnFrame, side=LEFT)

if telegramVar.get() == 0:
	testTelegramBtn.config(state="disabled")
	tokenBox.config(state="disabled")
	chatIDBox.config(state="disabled")

#If telegram is enabled, alert user that bot was started
initializeBot()

#Start concurrent threads
historyRefreshThread = threading.Thread(target=historyReresh)
historyRefreshThread.daemon = True
historyRefreshThread.start()

root.mainloop()



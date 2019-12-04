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
	#Check if this is a first time run
	with open('firstRun.txt', 'rb') as f:
		isFirstRun = pickle.load(f)

	if isFirstRun == 0:
		messagebox.showinfo("Hello World", "Welcome to 1Click Cos Bot")
		with open('firstRun.txt', 'wb') as f:
			pickle.dump(1, f)

	#Check if valid API keys are available
	with open('gridSettings.conf', 'rb') as f:
		quotesPair, tradePair, publicKey, privateKey, orderSize, gridDistance, lowerPrice, higherPrice, numberGrids = pickle.load(f)

	testExchange = exchangeInfo(publicKey, privateKey)
	if testExchange.testKey():
		print("Valid API keys loaded")
	else:
		messagebox.showinfo("Invalid", "API keys are invalid, please update them in the strategy tab.")

	#Load telegram settings
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
		sendTelegramMessage("An instance of your 1Click COS bot was just launched. If this wasn't you please login to your COSS account and disable your API keys immediately.", False)

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
	gridStratFrame.place(relwidth=FRAMEWIDTH*0.9, relheight=FRAMEHEIGHT/1.9, relx=FRAMEPADX*1.4, rely=FRAMEPADY*3.1)

	#Load all grid strategy settings
	# Load Grid Settings: publicKey, privateKey, orderSize, gridDistance, lowerPrice, higherPrice, numberOfGrids
	with open('gridSettings.conf', 'rb') as f:  # Python 3: open(..., 'rb')
		quotesPair, tradePair, publicKey, privateKey, orderSize, gridDistance, lowerPrice, higherPrice, numberGrids = pickle.load(f)
	quotePair.set(quotesPair)
	publicAPIKeyBox.delete(0, tk.END)
	publicAPIKeyBox.insert(tk.END, publicKey)
	privateAPIKeyBox.delete(0, tk.END)
	privateAPIKeyBox.insert(tk.END, privateKey)
	orderSizeBox.delete('1.0', tk.END)
	orderSizeBox.insert(tk.END, orderSize)
	gridDistanceBox.delete('1.0', tk.END)
	gridDistanceBox.insert(tk.END, gridDistance)
	lowerPriceBox.delete('1.0', tk.END)
	lowerPriceBox.insert(tk.END, lowerPrice)
	higherPriceBox.delete('1.0', tk.END)
	higherPriceBox.insert(tk.END, higherPrice)
	numberOfGrids.set(numberGrids)
	quotePairChanged(None)
	tradingPairChanged(None, tradePair)

#Create function for run button
def openRun():
	'''
	Switches frames to the run tab
	'''	
	openSettings()
	clearFrames()
	runBtn.config(bg=BTNCLICKEDBG, fg=BTNCLICKEDFG)

	#Update information in text fields
	runStrategyBox.config(state="normal")
	runStrategyBox.delete('1.0', tk.END)
	runStrategyBox.insert(tk.END, tradingStrat.get())
	runStrategyBox.config(state="disabled")
	runTradePairBox.config(state="normal")
	runTradePairBox.delete('1.0', tk.END)
	runTradePairBox.insert(tk.END, tradingPair.get() + "_" + quotePair.get())
	runTradePairBox.config(state="disabled")
	runInstanceNameBox.delete('1.0', tk.END)
	runInstanceNameBox.insert(tk.END, tradingStrat.get().replace(" ", "") + "_" + tradingPair.get().replace(" ", "") + "_" + quotePair.get().replace(" ", ""))

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

	with open("history.txt", "rb") as f:
		f.seek(0)
		historyTextField.delete("1.0", tk.END)
		historyTextField.insert(tk.END, f.read())

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
		with open("history.txt", "rb") as f2:
			f2.seek(0)
			historyTextField.delete("1.0", tk.END)
			historyTextField.insert(tk.END, f2.read())
		time.sleep(1)

def tradingPairChanged(event, pair):
	'''
	Update settings page with new trading pair
	'''
	if pair != "blank":
		tradingPair.set(pair)
	tradePairBalanceLabel.config(text="    Trade Balance (" + tradingPair.get() + ")")

def quotePairChanged(event):

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
	tradingPairChanged(None, "blank")

	quotePairBalanceLabel.config(text="    Quote Balance (" + quotePair.get() + ")")
	orderSizeLabel.config(text="    Order Size (" + quotePair.get() + ")")
	priceRangeLabel.config(text="    Price Range (" + quotePair.get() + ")")
	gridDistanceLabel.config(text="    Grid Distance (" + quotePair.get() + ")")

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
	if testKeys.testKey():
		messagebox.showinfo("Saved", "Your strategy settings will be applied")
	else:
		messagebox.showinfo("Invalid", "Looks like you entered invalid API keys, please try again")
		return 0

	#Save all settings to gridSettings.conf
	with open('gridSettings.conf', 'wb') as f:
	    pickle.dump([quotePair.get().strip(), tradingPair.get().strip(), testPublicKey, testPrivateKey, orderSizeBox.get("1.0", tk.END).strip(), gridDistanceBox.get("1.0", tk.END).strip(), lowerPriceBox.get("1.0", tk.END).strip(), higherPriceBox.get("1.0", tk.END).strip(), numberOfGrids.get()], f)
	openRun()
	return 1

def startStrategy():
	
	strategyWithArg = partial(strategyThread, runInstanceNameBox.get("1.0", tk.END).replace(" ", ""))
	strategyTestThread = threading.Thread(target=strategyWithArg)
	strategyTestThread.daemon = True
	strategyTestThread.start()

	openHistory()

def strategyThread(name):
	myGridBot = gridBotStart
	myGridBot.gridStart(name)

def demoCheckBoxChanged():
	if demoVar.get() == 0:
		print("Demo Mode disabled")
	else:
		print ("Demo Mode enabled")

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

try:
	connectionStatus = myExchange.checkConnection()
	print("Connected to exchange")
except:
	messagebox.showinfo("Error", "There was an error connecting to the exchange, please check your internet connection. Application will now exit.")
	exit(0)

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
img = ImageTk.PhotoImage(Image.open("coss.png"))
homeBtn = tk.Button(root, text="Home", padx=10, pady=5, fg=BTNCLICKEDFG, bg=BTNCLICKEDBG, height=1, width=4, command=openHome, relief=FLAT)
runBtn = tk.Button(root, text="Run", padx=10, pady=5, fg=BTNFG, bg=BTNBG, height=1, width=4, command=openRun, relief=FLAT)
settingsBtn = tk.Button(root, text="Strategy", padx=10, pady=5, fg=BTNFG, bg=BTNBG, height=1, width=4, command=openSettings, relief=FLAT)
historyBtn = tk.Button(root, text="History", padx=10, pady=5, fg=BTNFG, bg=BTNBG, height=1, width=4, command=openHistory, relief=FLAT)
botOptionBtn = tk.Button(root, text="Settings", padx=12, pady=5, fg=BTNFG, bg=BTNBG, height=1, width=4, command=openOptions, relief=FLAT)
aboutBtn = tk.Button(root, text="About", padx=10, pady=5, fg=BTNFG, bg=BTNBG, height=1, width=4, command=openAbout, relief=FLAT)
exchangeBtn = tk.Button(root, text="Extras", padx=14, pady=5, fg="white", bg="#663399", height=1, width=4, command=openAbout, relief=FLAT)

#Define Home page UI elements
homeInfo = tk.Text(homeFrame, relief=FLAT, fg=FOREGROUND, bg=BACKGROUND, height=24, width=47)
homeInfo.pack()
homeInfo.insert(tk.END, "\n1Click COSS Bot - version 0.1\n\nTo get started please first customize your bot\nfrom the strategy tab. You can also enable\ntelegram messaging from the settings tab.")
homeInfo.insert(tk.END, "\n\nOnce configured you can run the bot from the\nrun tab")
homeInfo.insert(tk.END, "\n\nLatest Updates (12/03/2019)\n---------------------------\n - First live build of 1Click COSS bot\n - Added support for grid strategy\n - Added Settings page to customize bot\n - Added History page to keep track of trades\n - Added UI for ease of use")
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
saveBtn = tk.Button(saveStratFrame, text="Save", padx=10, pady=5, fg=BTNFG, bg=BTNBG, height=1, width=4, command=saveStrategy, relief=FLAT)
saveBtn.pack()
#tk.Label(saveStratFrame, text="This strategy is not yet implemented", bg="#482923", fg=FOREGROUND).pack()

#Define UI elements for Buy Low Sell High Strategy Frame
blStratFrame = tk.Frame(root, bg="#482923")
tk.Label(blStratFrame, text="This strategy is not yet implemented", bg="#482923", fg=FOREGROUND).pack()

#Define UI elements for GRID Strategy Frame
gridStratFrame = tk.Frame(root, bg="#182923")
tk.Label(gridStratFrame, text="                         ", bg="#182923").grid(row=0, column=1)
tk.Label(gridStratFrame, text="Available Balances", bg="#182923", fg=FOREGROUND, font='Helvetica 8 bold').grid(row=1, column=1)

tradePairBalanceLabel = tk.Label(gridStratFrame, text="    Trade Balance (" + tradingPair.get() + ")")
tradePairBalanceLabel.config(relief=FLAT, bg="#182923", fg=FOREGROUND)
tradePairBalanceLabel.grid(row=2, column=0, sticky="W")
tradePairBalanceBox = tk.Text(gridStratFrame, width=12, height=1)
tradePairBalanceBox.insert(tk.END, "30000")
tradePairBalanceBox.config(state="disabled", bg="#182923", fg=FOREGROUND)
tradePairBalanceBox.grid(row=2, column=2)

quotePairBalanceLabel = tk.Label(gridStratFrame, text="    Quote Balance (" + quotePair.get() + ")")
quotePairBalanceLabel.config(relief=FLAT, bg="#182923", fg=FOREGROUND)
quotePairBalanceLabel.grid(row=3, column=0, sticky="W")
quotePairBalanceBox = tk.Text(gridStratFrame, width=12, height=1)
quotePairBalanceBox.insert(tk.END, "2.67")
quotePairBalanceBox.config(state="disabled", bg="#182923", fg=FOREGROUND)
quotePairBalanceBox.grid(row=3, column=2)

tk.Label(gridStratFrame, text="                         ", bg="#182923").grid(row=4, column=1)
tk.Label(gridStratFrame, text="Grid Settings", bg="#182923", fg=FOREGROUND, font='Helvetica 8 bold').grid(row=5, column=1)

orderSizeLabel = tk.Label(gridStratFrame, text="    Order Size (" + quotePair.get() + ")")
orderSizeLabel.config(relief=FLAT, bg="#182923", fg=FOREGROUND)
orderSizeLabel.grid(row=6, column=0, sticky="W")
orderSizeBox = tk.Text(gridStratFrame, width=12, height=1)
orderSizeBox.insert(tk.END, "0.015")
orderSizeBox.config(bg="white", fg="black")
orderSizeBox.grid(row=6, column=2)

gridDistanceLabel = tk.Label(gridStratFrame, text="    Grid Distance (" + quotePair.get() + ")")
gridDistanceLabel.config(relief=FLAT, bg="#182923", fg=FOREGROUND)
gridDistanceLabel.grid(row=7, column=0, sticky="W")
gridDistanceBox = tk.Text(gridStratFrame, width=12, height=1)
gridDistanceBox.insert(tk.END, "0.000001")
gridDistanceBox.config(bg="white", fg="black")
gridDistanceBox.grid(row=7, column=2)

priceRangeLabel = tk.Label(gridStratFrame, text="    Price Range (" + quotePair.get() + ")")
priceRangeLabel.config(relief=FLAT, bg="#182923", fg=FOREGROUND)
priceRangeLabel.grid(row=8, column=0, sticky="W")
lowerPriceBox = tk.Text(gridStratFrame, width=12, height=1)
lowerPriceBox.insert(tk.END, "0.000065")
lowerPriceBox.config(bg="#cc3300", fg="white")
lowerPriceBox.grid(row=8, column=1)
higherPriceBox = tk.Text(gridStratFrame, width=12, height=1)
higherPriceBox.insert(tk.END, "0.000095")
higherPriceBox.config(bg="#336600", fg="white")
higherPriceBox.grid(row=8, column=2)

gridNumberLabel = tk.Label(gridStratFrame, text="\n    Number Of Grids")
gridNumberLabel.config(relief=FLAT, bg="#182923", fg=FOREGROUND)
gridNumberLabel.grid(row=9, column=0, sticky="W")
numberOfGrids = Scale(gridStratFrame, from_=2, to=200, resolution=2, orient=HORIZONTAL, bg="#182923", fg=FOREGROUND, relief=FLAT, length=210)
numberOfGrids["highlightthickness"]=0
numberOfGrids.grid(row=9, column=1, columnspan=2)

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

runInstanceNameLabel = tk.Label(runFrame, text=" Name of Bot Instance:")
runInstanceNameLabel.config(relief=FLAT, bg=BACKGROUND, fg=FOREGROUND)
runInstanceNameLabel.grid(row=3, column=0, sticky="W")
runInstanceNameBox = tk.Text(runFrame, width=16, height=1)
runInstanceNameBox.config(state="normal", bg="white", fg="black")
runInstanceNameBox.grid(row=3, column=2, columnspan=2)

demoVar = tk.IntVar()
enableDemoChk = tk.Checkbutton(runFrame, text="Demo Mode", variable=demoVar, command=demoCheckBoxChanged)
enableDemoChk.config(bg=BACKGROUND, fg="red")
enableDemoChk.grid(row=4, sticky="W")

#Define bottom frame for run page start button
startRunFrame = tk.Frame(runFrame, bg=BACKGROUND)
startRunFrame.place(relwidth=FRAMEWIDTH*1.25, relheight=FRAMEHEIGHT/6.5, relx=0, rely=FRAMEPADY*7.2)
startBtn = tk.Button(startRunFrame, text="Start", padx=10, pady=5, fg=BTNFG, bg=BTNBG, height=1, width=4, command=startStrategy, relief=FLAT)
startBtn.pack()

#Define Options page UI elements
tk.Label(botOptionsFrame, text="       ", bg=BACKGROUND).grid(row=0, column=1)

telegramVar = tk.IntVar()
enableTelegramChk = tk.Checkbutton(botOptionsFrame, text="Telegram", variable=telegramVar, command=telegramCheckBoxChanged)
enableTelegramChk.config(bg=BACKGROUND, fg="red")
enableTelegramChk.grid(row=1, sticky="W")

testMessage_withArg = partial(sendTelegramMessage, "This is a test!", True)
testTelegramBtn = tk.Button(botOptionsFrame, text="Test and Save", padx=25, fg="white", bg="#082923", height=1, width=4, command=testMessage_withArg, relief=FLAT)
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
historyTextField = tk.Text(historyFrame, bg=BACKGROUND, fg=FOREGROUND, yscrollcommand=scroll.set, width=47, height=27.4)
historyTextField.grid(row=1, column=1, sticky="W")
scroll.config(command=historyTextField.yview)

#Setup UI elements
root.winfo_toplevel().title("1Click COSS Bot")

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



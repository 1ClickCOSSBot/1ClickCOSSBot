import os, sys
import pickle
import threading, time
import tkinter as tk
from tkinter import *
from tkinter import messagebox
from PIL import Image, ImageTk

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

def hide_me(event):
	event.widget.pack_forget()

def clearFrames():
	homeFrame.place_forget()
	settingsFrame.place_forget()
	runFrame.place_forget()
	aboutFrame.place_forget()
	historyFrame.place_forget()
	gridStratFrame.place_forget()
	blStratFrame.place_forget()
	homeBtn.config(bg="grey", fg="black")
	runBtn.config(bg="grey", fg="black")
	settingsBtn.config(bg="grey", fg="black")
	aboutBtn.config(bg="grey", fg="black")
	historyBtn.config(bg="grey", fg="black")

#Create function for run button
def openHome():
	'''
	Switches frames to the home tab
	'''	
	clearFrames()
	homeBtn.config(bg="blue", fg="white")
	homeFrame.place(relwidth=FRAMEHEIGHT, relheight=FRAMEWIDTH, relx=FRAMEPADX, rely=FRAMEPADY)

#Create function for settings button
def openSettings():
	'''
	Switches frames to the settings tab
	'''	
	clearFrames()
	settingsBtn.config(bg="blue", fg="white")
	settingsFrame.place(relwidth=FRAMEHEIGHT, relheight=FRAMEWIDTH, relx=FRAMEPADX, rely=FRAMEPADY)
	gridStratFrame.place(relwidth=FRAMEWIDTH*0.9, relheight=FRAMEHEIGHT/1.9, relx=FRAMEPADX*1.4, rely=FRAMEPADY*3.1)

	#Load all grid strategy settings
	# Load Grid Settings: publicKey, privateKey, orderSize, gridDistance, lowerPrice, higherPrice, numberOfGrids
	with open('gridSettings.conf', 'rb') as f:  # Python 3: open(..., 'rb')
		tradePair, publicKey, privateKey, orderSize, gridDistance, lowerPrice, higherPrice, numberGrids = pickle.load(f)
	tradingPair.set(tradePair)
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

	tradePairBalanceLabel.config(text="    Base Balance (" + tradingPair.get().split('_')[0] + ")")
	quotePairBalanceLabel.config(text="    Quote Balance (" + tradingPair.get().split('_')[1] + ")")
	orderSizeLabel.config(text="    Order Size (" + tradingPair.get().split('_')[1] + ")")
	priceRangeLabel.config(text="    Price Range (" + tradingPair.get().split('_')[1] + ")")
	gridDistanceLabel.config(text="    Grid Distance (" + tradingPair.get().split('_')[1] + ")")

#Create function for run button
def openRun():
	'''
	Switches frames to the run tab
	'''	
	clearFrames()
	runBtn.config(bg="blue", fg="white")
	runFrame.place(relwidth=FRAMEHEIGHT, relheight=FRAMEWIDTH, relx=FRAMEPADX, rely=FRAMEPADY)

#Create function for about button
def openAbout():
	'''
	Switches frames to the about tab
	'''	
	clearFrames()
	aboutBtn.config(bg="blue", fg="white")
	aboutFrame.place(relwidth=FRAMEHEIGHT, relheight=FRAMEWIDTH, relx=FRAMEPADX, rely=FRAMEPADY)

#Create function for history button
def openHistory():
	'''
	Switches frames to the about tab
	'''	
	clearFrames()
	historyBtn.config(bg="blue", fg="white")
	historyFrame.place(relwidth=FRAMEHEIGHT, relheight=FRAMEWIDTH, relx=FRAMEPADX, rely=FRAMEPADY)

	with open("history.txt", "rb") as f:
		f.seek(0)
		historyTextField.delete("1.0", tk.END)
		historyTextField.insert(tk.END, f.read())

def historyReresh():
    while True:
    	with open("history.txt", "rb") as f:
    		f.seek(0)
    		historyTextField.delete("1.0", tk.END)
    		historyTextField.insert(tk.END, f.read())
    	time.sleep(1)

def tradingPairChanged(event):
	'''
	Update settings page with new trading pair
	'''
	tradePairBalanceLabel.config(text="    Base Balance (" + tradingPair.get().split('_')[0] + ")")
	quotePairBalanceLabel.config(text="    Quote Balance (" + tradingPair.get().split('_')[1] + ")")
	orderSizeLabel.config(text="    Order Size (" + tradingPair.get().split('_')[1] + ")")
	priceRangeLabel.config(text="    Price Range (" + tradingPair.get().split('_')[1] + ")")
	gridDistanceLabel.config(text="    Grid Distance (" + tradingPair.get().split('_')[1] + ")")


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

	#Save all settings to gridSettings.conf
	with open('gridSettings.conf', 'wb') as f:
	    pickle.dump([tradingPair.get().strip(), publicAPIKeyBox.get().strip(), privateAPIKeyBox.get().strip(), orderSizeBox.get("1.0", tk.END).strip(), gridDistanceBox.get("1.0", tk.END).strip(), lowerPriceBox.get("1.0", tk.END).strip(), higherPriceBox.get("1.0", tk.END).strip(), numberOfGrids.get()], f)

	messagebox.showinfo("Saved", "Your strategy settings have been applied")
	openRun()

#Create the root UI
root = tk.Tk()
#root.configure(bg='#282923')
root.resizable(False, False)
if os.name == "nt":
	root.attributes('-alpha', 0.97)

#Define Main UI elements
canvas = tk.Canvas(root, height=CANVASHEIGHT, width=CANVASWIDTH, bg="#000000")
btnFrame = tk.Frame(root, bg="black")
homeFrame = tk.Frame(root, bg="#282923")
runFrame = tk.Frame(root, bg="#282923")
settingsFrame = tk.Frame(root, bg="#282923")
aboutFrame = tk.Frame(root,bg="#282923")
historyFrame = tk.Frame(root,bg="#282923")
notificationFrame = tk.Frame(root, bg="#282923")
img = ImageTk.PhotoImage(Image.open("coss.png"))
homeBtn = tk.Button(root, text="Home", padx=10, pady=5, fg="white", bg="blue", height=1, width=4, command=openHome, relief=FLAT)
runBtn = tk.Button(root, text="Run", padx=10, pady=5, fg="black", bg="grey", height=1, width=4, command=openRun, relief=FLAT)
settingsBtn = tk.Button(root, text="Settings", padx=10, pady=5, fg="black", bg="grey", height=1, width=4, command=openSettings, relief=FLAT)
aboutBtn = tk.Button(root, text="About", padx=10, pady=5, fg="black", bg="grey", height=1, width=4, command=openAbout, relief=FLAT)
historyBtn = tk.Button(root, text="History", padx=10, pady=5, fg="black", bg="grey", height=1, width=4, command=openHistory, relief=FLAT)

#Define Home page UI elements
homeInfo = tk.Text(homeFrame, relief=FLAT, fg="white", bg="#282923", height=24, width=47)
homeInfo.pack()
homeInfo.insert(tk.END, "\nWelcome to the 1Click COSS Bot\n\nTo get started please first customize your bot\nsettings from the settings tab")
homeInfo.insert(tk.END, "\n\nOnce configured you can run the bot from the\nrun tab")
homeInfo.insert(tk.END, "\n\nLatest Updates (11/21/2019)\n---------------------------\n - First live build of 1Click COSS bot\n - Added support for grid strategy\n - Added Settings page to customize bot\n - Added History page to keep track of trades\n - Added UI for ease of use")
homeInfo.insert(tk.END, "\n\nTrading is very risky, the use of this tool may\nresult in significant losses")
homeInfo.insert(tk.END, "\n\nTo protect your primary COSS account, always\ncreate a second account for use with public\ntrading bots.")
homeInfo.config(state="disabled")

if os.name == "nt":
	cossPhoto = ImageTk.PhotoImage(Image.open("coss2.png"))
	cossPhotoLabel = tk.Label(homeFrame,text="image",image=cossPhoto, bg="#282923")
	cossPhotoLabel.pack()
else:
	print("Images not supported in this OS") 

#Define Settings page UI elements
tk.Label(settingsFrame, text="", bg="#282923").grid(row=0)

publicLabel = tk.Label(settingsFrame, text="   Public Key")
publicLabel.config(relief=FLAT, bg="#282923", fg="white")
publicLabel.grid(row=1, sticky="W")
publicAPIKeyBox = tk.Entry(settingsFrame, show="*", width=46)
publicAPIKeyBox.grid(row=1, column=1)

privateLabel = tk.Label(settingsFrame, text="   Private Key")
privateLabel.config(relief=FLAT, bg="#282923", fg="white")
privateLabel.grid(row=2, sticky="W")
privateAPIKeyBox = tk.Entry(settingsFrame, show="*", width=46)
privateAPIKeyBox.grid(row=2, column=1)

tk.Label(settingsFrame, text="", bg="#282923").grid(row=3)

tradingPairText = tk.Label(settingsFrame, text="   Trading Pair")
tradingPairText.config(relief=FLAT, bg="#282923", fg="white")
tradingPairText.grid(row=4, column=0, sticky="W")
tradingPairOptions = [
    "COS_ETH",
    "COS_BTC",
    "ETH_BTC",
    "SATTY_USDT"
]
tradingPair = StringVar(settingsFrame)
tradingPair.set(tradingPairOptions[0]) # initial value
pairMenu = OptionMenu(*(settingsFrame, tradingPair) + tuple(tradingPairOptions), command=tradingPairChanged)
pairMenu.config(bg="#282923", fg="white", relief=FLAT)
pairMenu["menu"].config(bg="#282923", fg="white", relief=FLAT)
pairMenu["highlightthickness"]=0
pairMenu.grid(row=4, column=1)

tradingStratText = tk.Label(settingsFrame, text="   Trading Strategy")
tradingStratText.config(relief=FLAT, bg="#282923", fg="white")
tradingStratText.grid(row=5, column=0, sticky="W")
tradingStratOptions = [
    "GRID MM",
    "Buy Low Sell High"
]
tradingStrat = StringVar(settingsFrame)
tradingStrat.set(tradingStratOptions[0]) # initial value
stratMenu = OptionMenu(*(settingsFrame, tradingStrat) + tuple(tradingStratOptions), command=stratMenuChanged)
stratMenu.config(bg="#282923", fg="white", relief=FLAT)
stratMenu["menu"].config(bg="#282923", fg="white", relief=FLAT)
stratMenu["highlightthickness"]=0
stratMenu.grid(row=5, column=1)

#Define bottom frame for Settings page apply button
saveStratFrame = tk.Frame(settingsFrame, bg="#282923")
saveStratFrame.place(relwidth=FRAMEWIDTH*1.25, relheight=FRAMEHEIGHT/6.5, relx=0, rely=FRAMEPADY*7.2)
saveBtn = tk.Button(saveStratFrame, text="Save", padx=10, pady=5, fg="black", bg="grey", height=1, width=4, command=saveStrategy, relief=FLAT)
saveBtn.pack()
#tk.Label(saveStratFrame, text="This strategy is not yet implemented", bg="#482923", fg="white").pack()

#Define UI elements for Buy Low Sell High Strategy Frame
blStratFrame = tk.Frame(root, bg="#482923")
tk.Label(blStratFrame, text="This strategy is not yet implemented", bg="#482923", fg="white").pack()

#Define UI elements for GRID Strategy Frame
gridStratFrame = tk.Frame(root, bg="#182923")
tk.Label(gridStratFrame, text="                         ", bg="#182923").grid(row=0, column=1)
tk.Label(gridStratFrame, text="Available Balances", bg="#182923", fg="white", font='Helvetica 8 bold').grid(row=1, column=1)

tradePairBalanceLabel = tk.Label(gridStratFrame, text="    Base Balance (" + tradingPair.get().split('_')[0] + ")")
tradePairBalanceLabel.config(relief=FLAT, bg="#182923", fg="white")
tradePairBalanceLabel.grid(row=2, column=0, sticky="W")
tradePairBalanceBox = tk.Text(gridStratFrame, width=12, height=1)
tradePairBalanceBox.insert(tk.END, "30000")
tradePairBalanceBox.config(state="disabled", bg="#182923", fg="white")
tradePairBalanceBox.grid(row=2, column=2)

quotePairBalanceLabel = tk.Label(gridStratFrame, text="    Quote Balance (" + tradingPair.get().split('_')[1] + ")")
quotePairBalanceLabel.config(relief=FLAT, bg="#182923", fg="white")
quotePairBalanceLabel.grid(row=3, column=0, sticky="W")
quotePairBalanceBox = tk.Text(gridStratFrame, width=12, height=1)
quotePairBalanceBox.insert(tk.END, "2.67")
quotePairBalanceBox.config(state="disabled", bg="#182923", fg="white")
quotePairBalanceBox.grid(row=3, column=2)

tk.Label(gridStratFrame, text="                         ", bg="#182923").grid(row=4, column=1)
tk.Label(gridStratFrame, text="Grid Settings", bg="#182923", fg="white", font='Helvetica 8 bold').grid(row=5, column=1)

orderSizeLabel = tk.Label(gridStratFrame, text="    Order Size (" + tradingPair.get().split('_')[1] + ")")
orderSizeLabel.config(relief=FLAT, bg="#182923", fg="white")
orderSizeLabel.grid(row=6, column=0, sticky="W")
orderSizeBox = tk.Text(gridStratFrame, width=12, height=1)
orderSizeBox.insert(tk.END, "0.015")
orderSizeBox.config(bg="#352923", fg="white")
orderSizeBox.grid(row=6, column=2)

gridDistanceLabel = tk.Label(gridStratFrame, text="    Grid Distance (" + tradingPair.get().split('_')[1] + ")")
gridDistanceLabel.config(relief=FLAT, bg="#182923", fg="white")
gridDistanceLabel.grid(row=7, column=0, sticky="W")
gridDistanceBox = tk.Text(gridStratFrame, width=12, height=1)
gridDistanceBox.insert(tk.END, "0.000001")
gridDistanceBox.config(bg="#352923", fg="white")
gridDistanceBox.grid(row=7, column=2)

priceRangeLabel = tk.Label(gridStratFrame, text="    Price Range (" + tradingPair.get().split('_')[1] + ")")
priceRangeLabel.config(relief=FLAT, bg="#182923", fg="white")
priceRangeLabel.grid(row=8, column=0, sticky="W")
lowerPriceBox = tk.Text(gridStratFrame, width=12, height=1)
lowerPriceBox.insert(tk.END, "0.000065")
lowerPriceBox.config(bg="#722123", fg="white")
lowerPriceBox.grid(row=8, column=1)
higherPriceBox = tk.Text(gridStratFrame, width=12, height=1)
higherPriceBox.insert(tk.END, "0.000095")
higherPriceBox.config(bg="#001923", fg="white")
higherPriceBox.grid(row=8, column=2)

gridNumberLabel = tk.Label(gridStratFrame, text="    Number Of Grids")
gridNumberLabel.config(relief=FLAT, bg="#182923", fg="white")
gridNumberLabel.grid(row=9, column=0, sticky="W")
numberOfGrids = Scale(gridStratFrame, from_=2, to=200, resolution=2, orient=HORIZONTAL, bg="#182923", fg="white", relief=FLAT)
numberOfGrids["highlightthickness"]=0
numberOfGrids.grid(row=9, column=2)

#gridLowerPrice
#gridUpperPrice

#Define Run page UI elements

#Define About page UI elements
aboutInfo = tk.Text(aboutFrame, relief=FLAT, fg="white", bg="#282923", height=24, width=47)
aboutInfo.pack()
aboutInfo.insert(tk.END, "\nBot created by Omer \nTelegram: @omer259\nReddit: https://www.reddit.com/user/Omer259/")
aboutInfo.insert(tk.END, "\n\nBitcoin Donation Address: \nbc1qnjcnhcex50659vxnuhdkuzhhu4m0ewmx6p43j2")
aboutInfo.insert(tk.END, "\n\nEthereum Donation Address: \n0xE9b79A87520DFB16824d9AfC40a7d8bC1a81a753")
aboutInfo.insert(tk.END, "\n\nAll trading performed using this bot is\nat your own risk. I will not be held\nresponsible for any gains or losses caused by\nthe use of this tool")
aboutInfo.config(state="disabled")

#Define History page UI elements
scroll = Scrollbar(historyFrame)
scroll.grid(row=1, column=2, sticky="W", ipady=191.70)
tk.Label(historyFrame, text="", bg="#282923").grid(row=0, column=0)
historyTextField = tk.Text(historyFrame, bg="#282923", fg="white", yscrollcommand=scroll.set, width=47, height=27.4)
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
homeBtn.config(bg="blue")
runBtn.pack(in_=btnFrame, side=LEFT)
settingsBtn.pack(in_=btnFrame, side=LEFT)
historyBtn.pack(in_=btnFrame, side=LEFT)
aboutBtn.pack(in_=btnFrame, side=LEFT)

#Start concurrent threads
historyRefreshThread = threading.Thread(target=historyReresh)
historyRefreshThread.daemon = True
historyRefreshThread.start()

root.mainloop()



import os, sys
import tkinter as tk
from tkinter import *
from PIL import Image, ImageTk

'''
Pre-Reqs
--------
pip install Pillow

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
	homeBtn.config(relief=RAISED)
	runBtn.config(relief=RAISED)
	settingsBtn.config(relief=RAISED)
	aboutBtn.config(relief=RAISED)
	historyBtn.config(relief=RAISED)

#Create function for run button
def openHome():
	'''
	Switches frames to the home tab
	'''	
	clearFrames()
	homeBtn.config(relief=SUNKEN)
	homeFrame.place(relwidth=FRAMEHEIGHT, relheight=FRAMEWIDTH, relx=FRAMEPADX, rely=FRAMEPADY)

#Create function for settings button
def openSettings():
	'''
	Switches frames to the settings tab
	'''	
	clearFrames()
	settingsBtn.config(relief=SUNKEN)
	settingsFrame.place(relwidth=FRAMEHEIGHT, relheight=FRAMEWIDTH, relx=FRAMEPADX, rely=FRAMEPADY)

#Create function for run button
def openRun():
	'''
	Switches frames to the run tab
	'''	
	clearFrames()
	runBtn.config(relief=SUNKEN)
	runFrame.place(relwidth=FRAMEHEIGHT, relheight=FRAMEWIDTH, relx=FRAMEPADX, rely=FRAMEPADY)

#Create function for about button
def openAbout():
	'''
	Switches frames to the about tab
	'''	
	clearFrames()
	aboutBtn.config(relief=SUNKEN)
	aboutFrame.place(relwidth=FRAMEHEIGHT, relheight=FRAMEWIDTH, relx=FRAMEPADX, rely=FRAMEPADY)

#Create function for history button
def openHistory():
	'''
	Switches frames to the about tab
	'''	
	clearFrames()
	historyBtn.config(relief=SUNKEN)
	historyFrame.place(relwidth=FRAMEHEIGHT, relheight=FRAMEWIDTH, relx=FRAMEPADX, rely=FRAMEPADY)

#Create the root UI
root = tk.Tk()
root.configure(bg='#282923')
root.resizable(False, False)

#Define Main UI elements
canvas = tk.Canvas(root, height=CANVASHEIGHT, width=CANVASWIDTH, bg="#000000")
btnFrame = tk.Frame(root, bg="black")
homeFrame = tk.Frame(root, bg="#282923")
runFrame = tk.Frame(root, bg="#282923")
settingsFrame = tk.Frame(root, bg="#282923")
aboutFrame = tk.Frame(root,bg="#282923")
historyFrame = tk.Frame(root,bg="#282923")
img = ImageTk.PhotoImage(Image.open("coss.png"))
homeBtn = tk.Button(root, text="Home", padx=10, pady=5, fg="black", bg="grey", height=1, width=4, command=openHome)
runBtn = tk.Button(root, text="Run", padx=10, pady=5, fg="black", bg="grey", height=1, width=4, command=openRun)
settingsBtn = tk.Button(root, text="Settings", padx=10, pady=5, fg="black", bg="grey", height=1, width=4, command=openSettings)
aboutBtn = tk.Button(root, text="About", padx=10, pady=5, fg="black", bg="grey", height=1, width=4, command=openAbout)
historyBtn = tk.Button(root, text="History", padx=10, pady=5, fg="black", bg="grey", height=1, width=4, command=openHistory)

#Define Home page UI elements
homeInfo = tk.Text(homeFrame, relief=FLAT, fg="white", bg="#282923", height=18, width=47)
homeInfo.pack()
homeInfo.insert(tk.END, "\nWelcome to the 1Click COSS Bot\n\nTo get started please first customize your bot\nsettings from the settings tab")
homeInfo.insert(tk.END, "\n\nOnce configured you can run the bot from the\nrun tab")
homeInfo.insert(tk.END, "\n\nLatest Updates\n--------------\n - First live build of 1Click COSS bot\n - Added support for grid strategy\n - Added Settings page to customize bot\n - Added History page to keep track of trades\n - Added UI for ease of use")


#Define Settings page UI elements
tk.Label(settingsFrame, text="", bg="#282923").grid(row=0)

publicLabel = tk.Label(settingsFrame, text="   Public Key")
publicLabel.config(relief=FLAT, bg="#282923", fg="white")
publicLabel.grid(row=1)
publicAPIKeyBox = tk.Entry(settingsFrame, show="*", width=46)
publicAPIKeyBox.grid(row=1, column=1)

privateLabel = tk.Label(settingsFrame, text="   Private Key")
privateLabel.config(relief=FLAT, bg="#282923", fg="white")
privateLabel.grid(row=2)
privateAPIKeyBox = tk.Entry(settingsFrame, show="*", width=46)
privateAPIKeyBox.grid(row=2, column=1)

tk.Label(settingsFrame, text="", bg="#282923").grid(row=3)

tradingPairText = tk.Label(settingsFrame, text="   Trading Pair")
tradingPairText.config(relief=FLAT, bg="#282923", fg="white")
tradingPairText.grid(row=4, column=0)
tradingPairOptions = [
    "COS_ETH",
    "COS_BTC",
    "ETH_BTC"
]
tradingPair = StringVar(settingsFrame)
tradingPair.set(tradingPairOptions[0]) # initial value
pairMenu = OptionMenu(*(settingsFrame, tradingPair) + tuple(tradingPairOptions))
pairMenu.config(bg="#282923", fg="white", relief=FLAT)
pairMenu["menu"].config(bg="#282923", fg="white", relief=FLAT)
pairMenu["highlightthickness"]=0
pairMenu.grid(row=4, column=1)

tradingStratText = tk.Label(settingsFrame, text="   Trading Strategy")
tradingStratText.config(relief=FLAT, bg="#282923", fg="white")
tradingStratText.grid(row=5, column=0)
tradingStratOptions = [
    "GRID MM",
    "Buy Low Sell High"
]
tradingStrat = StringVar(settingsFrame)
tradingStrat.set(tradingStratOptions[0]) # initial value
stratMenu = OptionMenu(*(settingsFrame, tradingStrat) + tuple(tradingStratOptions))
stratMenu.config(bg="#282923", fg="white", relief=FLAT)
stratMenu["menu"].config(bg="#282923", fg="white", relief=FLAT)
stratMenu["highlightthickness"]=0
stratMenu.grid(row=5, column=1)

#Define Run page UI elements

#Define About page UI elements
aboutInfo = tk.Text(aboutFrame, relief=FLAT, fg="white", bg="#282923", height=18, width=47)
aboutInfo.pack()
aboutInfo.insert(tk.END, "\nBot created by Omer \nTelegram: @omer259\nReddit: https://www.reddit.com/user/Omer259/")
aboutInfo.insert(tk.END, "\n\nBitcoin Donation Address: \nbc1qnjcnhcex50659vxnuhdkuzhhu4m0ewmx6p43j2")
aboutInfo.insert(tk.END, "\n\nEthereum Donation Address: \n0xE9b79A87520DFB16824d9AfC40a7d8bC1a81a753")

#Define History page UI elements

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
homeBtn.config(relief=SUNKEN)
runBtn.pack(in_=btnFrame, side=LEFT)
settingsBtn.pack(in_=btnFrame, side=LEFT)
historyBtn.pack(in_=btnFrame, side=LEFT)
aboutBtn.pack(in_=btnFrame, side=LEFT)

root.mainloop()



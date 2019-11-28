from glob import glob

print("This is a test file")

if glob("history/*__history.txt"):
	print("This file exists")

existingFiles = glob("history/*__history.txt")

file1 = existingFiles[0]

print(file1.split("\\")[1])
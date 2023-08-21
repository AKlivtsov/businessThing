import os 

def pathCheck(dirList):
	for item in dirList:
		if "." not in item:
			newPath = os.getcwd() + '/' + item
			newList = os.listdir(newPath)

			for newItem in newList:
				if "." in newItem:
					mainList.append(item + '/' + newItem)

				else:
					pathCheck(newList)
 
mainList = os.listdir()

pathCheck(mainList)
		

print(mainList)

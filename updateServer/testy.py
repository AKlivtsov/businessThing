import os 

def clear():
	for item in mainList:
		if "." not in item:
			mainList.pop(mainList.index(item))
			clear()

def pathCheck(dirList, startPath):
	for item in dirList:
		if "." not in item:
			newPath = startPath + '/' + item

			if os.path.isfile(newPath):
				pass

			else:
				newList = os.listdir(newPath)

				for newItem in newList:
					pathToCheck = []

					if "." in newItem:
						mainList.append(item + '/' + newItem)

					else:
						pathToCheck.append(item + '/' + newItem)

					if pathToCheck:
						for path in  pathToCheck:
							anoPath = startPath +'/' 
							pathCheck(pathToCheck, anoPath)
	
	return True		

path = 'D:/!SubieProjects/businessThing/updateServer/testFolder'

mainList = os.listdir(path)
state = pathCheck(mainList, path)

if state:
	clear()
	print(mainList)


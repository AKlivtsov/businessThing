import os 

def pathCheck(dirList, startPath):
	for item in dirList:
		if "." not in item:
			newPath = startPath + '/' + item
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

			

path = 'C:/Users/sasha/OneDrive/Рабочий стол/gfhjg'

mainList = os.listdir(path)
pathCheck(mainList, path)
		
print(mainList)


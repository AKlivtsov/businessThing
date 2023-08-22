import os 

def clear():
	for item in listOfFiles:
		if "." not in item:
			del listOfFiles[listOfFiles.index(item)]
			clear()

def pathCheck(dirList, startPath):
	for item in dirList:
		if "." not in item:
			newPath = startPath + '/' + item

			if not os.path.isfile(newPath):
				newList = os.listdir(newPath)

				for newItem in newList:
					pathToCheck = []

					if "." in newItem:
						listOfFiles.append(item + '/' + newItem)

					else:
						pathToCheck.append(item + '/' + newItem)

					if pathToCheck:
						for path in  pathToCheck:
							anoPath = startPath +'/' 
							pathCheck(pathToCheck, anoPath)
	
	return True		

path = 'testFolder'

listOfFiles = os.listdir(path)
state = pathCheck(listOfFiles, path)

if state:
	clear()
	foldersList = []

	for file in listOfFiles:
		if "/" in file:
			fileName = file.split("/")[-1]
			folders = file.replace(fileName, '')
			foldersList.append(folders)

	# remove copies 
	foldersList = list(set(foldersList))
	foldersList.sort()

	for folders in foldersList:
		os.makedirs("exportFolder/" + folders)


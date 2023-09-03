import tarfile as tar
import sqlite3


folder = str(input("enter folder name: "))
archiveName = folder + '.tar'

version = float(input("enter prog version (float): "))

archive = tar.open(archiveName, 'x:gz')

if '/' not in folder:
	archive.add(folder + '/')
else:
	archive.add(folder)


connect = sqlite3.connect("server.db")
cursor = connect.cursor()
cursor.execute("UPDATE server SET path = ?, version = ? WHERE ROWID = ?", (archiveName, version, 1))
connect.commit()

print('done!') 

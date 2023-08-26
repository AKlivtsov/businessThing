import tarfile as tar

archive = tar.open("ver1.2.tar", 'x:gz')
archive.add('D:/!SubieProjects/businessThing/main')

# archive = tar.open("update", 'r:gz')

# archive.extractall('exportFolder/')

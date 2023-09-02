import tarfile as tar

archive = tar.open("ver1_3.tar", 'x:gz')
archive.add('ver1_3/')

# archive = tar.open("update", 'r:gz')

# archive.extractall('exportFolder/')

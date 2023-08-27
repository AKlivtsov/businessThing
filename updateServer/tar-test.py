import tarfile as tar

archive = tar.open("ver1_2.tar", 'x:gz')
archive.add('ver1_2/')

# archive = tar.open("update", 'r:gz')

# archive.extractall('exportFolder/')

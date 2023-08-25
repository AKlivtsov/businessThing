import tarfile as tar

archive = tar.open("update.tar", 'x:gz')
archive.add('testFolder/')

# archive = tar.open("update", 'r:gz')

# archive.extractall('exportFolder/')

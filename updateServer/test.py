filename = 'ver12312313.tar'

fileName = filename.split(".")[-1]
path = filename.replace(f'.{fileName}', '')

print(path)

import re
import os

file = os.open('main.c', os.O_RDWR)
print(file)
readed = file.read()

stripped = re.sub("[/*].*[*/]", "", readed)

newTest = os.write('test.c', stripped)



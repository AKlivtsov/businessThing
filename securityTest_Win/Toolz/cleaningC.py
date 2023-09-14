import re
import os

file = open('main.c', 'r+')
readed = file.read()

stripped = re.sub("[/*].* [*/]", "", readed)

newTest = open('test5.c', 'w')
newTest.write(stripped) 



import re
import os

import re


def remove_comments(text):
    # Создаем регулярное выражение для удаления однострочных комментариев
    single_line_comment_pattern = re.compile(r'/\*(.*?)\*/', re.DOTALL)

    # Удаляем однострочные комментарии
    cleansed_text = single_line_comment_pattern.sub('', text)


    # Создаем регулярное выражение для удаления многострочных комментариев 
    multi_line_comment_pattern = re.compile(r'(/\*).*?(\*/)', re.DOTALL)

    # Заменяем многострочные комментарии на пробелы
    cleansed_text = multi_line_comment_pattern.sub('\\1 \\2', cleansed_text, re.S)

    return cleansed_text


file = open('main.c', 'r+')
readed = file.read()

stripped = remove_comments(readed)

newfile = open('main.c', 'w')
newfile.write(stripped) 



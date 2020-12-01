#!/usr/local/bin/python3
#-*- coding: utf-8 -*-
# Глава 15. Сервер PyMailCGI.
# Отправка почты по SMTP.
# Использование сценария отправки почты без браузера.
# Пример 16.5 (Лутц Т2 стр.609)
"""
# ---------------------------------------------------------------------------- #
Отправляет почтовое сообщение, конструируя из входных данных адрес URL
следующего вида:
http://servername/pathname/onEditPageSend.py?site=smtp.rmi.net&
											 From=lutz@rmi.net&
											 To=lutz@rmi.net&
											 Subject=test+url&
											 text=Hello+Mark;this+Mark
# ---------------------------------------------------------------------------- #
"""

from urllib.request import urlopen
from urllib.parse import quote_plus

url = 'http://localhost:8000/cgi-bin/onEditPageSend.py'
url += '?site=%s' % quote_plus(input('Site>'))
url += '?From=%s' % quote_plus(input('From>'))
url += '?To=%s' % quote_plus(input('To>'))
url += '?Subject=%s' % quote_plus(input('Sibj>'))
url += '?text=%s' % quote_plus(input('text>'))					# или цикл ввода

print('Reply html:')
print(urlopen(url).read().decode())								# страница пожтверждения или с сообщением об ошибке
#!/usr/local/bin/python3
#-*- coding: utf-8 -*-
# Глава 15. Сервер PyMailCGI.
# Чтение электронной почты по протоколу POP.
# Страница выбора почты из списка.
# Пример 16.7 (Лутц Т2 стр.613)
"""
# ---------------------------------------------------------------------------- #
Вызывается при отправке пароля POP из окна ввода: создает страницу
со списком входящей почты;

в 2.0+ загружаются только заголовки писем, позднее, по запросу, загружается
полный текст только одного выбранного сообщения; однако нам по-прежнему
необходимо загружать все заголовки всякий раз, когда создается страница
с оглавлением: для реализации кеширования сообщений на стороне сервера
может потребоваться использовать базу данных на стороне сервера (?)
и ключ сеанса или использовать какие-то другие механизмы;
3.0: выполняет декодирование заголовков перед отображением списка,
однако принтер и браузер должны уметь обрабатывать их;
# ---------------------------------------------------------------------------- #
"""

import cgi
import loadmail, commonhtml
from externs import mailtools
from secret import encode									# модуль шифрования, определяемый пользователем

MaxHdr = 35													# максимальная длина заголовков в списке

# с предыдущей страницы поступает пароль, остальное обычно в модуле
formdata = cgi.FieldStorage()
mailuser, mailpswd, mailsite = commonhtml.getstandardpopfields(formdata)
parser = mailtools.MailParser()

try:
	newmails = loadmail.loadmailhdrs(mailsite, mailuser, mailpswd)
	mailnum = 1
	maillist = []											# или использовать enumerate
	for mail in newmails:									# списко заголовков
		msginfo = []
		hdrs = parser.parseHeaders(mail)					# email.message.Message
		addrhdrs = ('From', 'To', 'Cc', 'Bcc')				# декодировать только имена
		for key in ('Subject', 'From', 'Date'):
			rawhdr = hdrs.get(key, '?')
			if key not in addrhdrs:
				dechdr = parser.decodeHeader(rawhdr)		# 3.0: декодировать для отображения
			else:											# закодировать при отправке
				dechdr = parser.decodeAddrHeader(rawhdr)	# только имена
			msginfo.append(dechdr[:MaxHdr])
		msginfo = ' | '.join(msginfo)
		maillist.append((msginfo, commonhtml.urlroot + 'onViewListLink.py',
								  {'mnum': mailnum,
								   'user': mailuser,		# параметры передаются в URL, а не в полях
								   'pswd': encode(mailpswd),
								   'site': mailsite}))
		mailnum += 1
	commonhtml.listpage(maillist, 'mail selection list')
except:
	commonhtml.errorpage('Error loading mail index')

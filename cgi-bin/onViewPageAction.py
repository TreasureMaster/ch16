#!/usr/local/bin/python3
#-*- coding: utf-8 -*-
# Глава 15. Сервер PyMailCGI.
# Обработка загруженной почты.
# Пример 16.9 (Лутц Т2 стр.631)
"""
# ---------------------------------------------------------------------------- #
Вызывается при отправке формы в окне просмотра сообщения: выполняет
выбранное действие = (fwd, reply, delete);
в 2.0+ повторно используется логика удаления в пакете mailtools,
первоначально реализованная для PyMailGUI;
# ---------------------------------------------------------------------------- #
"""

import cgi, commonhtml, secret
from externs import mailtools, mailconfig
from commonhtml import  getfield

def quotetext(form):
	"""
	обратите внимание, что заголовки поступают из формы предыдущей страницы,
	а не получаются в результате повторного анализа почтового сообщения;
	это означает, что функция commonhtml.viewpage должна передавать дату
	в скрытом поле
	"""
	parser = mailtools.MailParser()
	addrhdrs = ('From', 'To', 'Cc', 'Bcc')							# декодируется только имя
	quoted = '\n-----Original Message-----\n'
	for hdr in ('From', 'To', 'Date'):
		rawhdr = getfield(form, hdr)
		if hdr not in addrhdrs:
			dechdr = parser.decodeHeader(rawhdr)					# 3.0: декодировать для отображения
		else:														# закодировать при отправке
			dechdr = parser.decodeAddrHeader(rawhdr)				# только имена в адресах
		quoted += '%s: %s\n' % (hdr, dechdr)
	quoted += '\n' + getfield(form, 'text')
	quoted = '\n' + quoted.replace('\n', '\n> ')
	return quoted

form = cgi.FieldStorage()
user, pswd, site = commonhtml.getstandardpopfields(form)
pswd = secret.decode(pswd)

try:
	if form['action'].value == 'Reply':
		headers = {'From': mailconfig.myaddress,					# 3.0: декодирование выполняет commonhtml
				   'To': getfield(form, 'From'),
				   'Cc': mailconfig.myaddress,
				   'Subject': 'Re: ' + getfield(form, 'Subject')}
		commonhtml.editpage('Reply', headers, quotetext(form))

	elif form['action'].value == 'Forward':
		headers = {'From': mailconfig.myaddress,
				   'To': '',
				   'Cc': mailconfig.myaddress,
				   'Subject': 'Fwd: ' + getfield(form, 'Subject')}
		commonhtml.editpage('Forward', headers, quotetext(form))

	elif form['action'].value == 'Delete':							# поле mnum необходимо здесь
		msgnum = int(form['mnum'].value)
		fetcher = mailtools.SilentMailFetcher(site, user, pswd)
		fetcher.deleteMessage([msgnum])
		commonhtml.confirmationpage('Delete')

	else:
		assert False, 'Invalid view action requested'
except:
	commonhtml.errorpage('Cannot process view action')
#!/usr/local/bin/python3
#-*- coding: utf-8 -*-
# Глава 15. Сервер PyMailCGI.
# Чтение электронной почты по протоколу POP.
# Страница просмотра сообщений.
# Пример 16.8 (Лутц Т2 стр.623)
"""
# ---------------------------------------------------------------------------- #
Вызывается щелчком мыши на ссылке, указывающей на сообщение в главном списке:
создает страницу просмотра;

конструктор cgi.FieldStorage преобразует экранированные последовательности
в ссылках с помощью urllib.parse (%xx и '+', замещающие пробелы, уже
преобразованы обратно); в 2.0+ здесь загружается только одно сообщение,
а не весь список; в 2.0+ мы также отыскиваем осоновную текстовую часть
сообщения, вместо того чтобы вслепую отображать полный текст (со всеми
вложениями), и генерируем ссылки на файлы вложений, сохраненные на сервере;
сохранение файлов вложений возможно только для 1 пользователя и 1 сообщения;
большая часть улучшений в 2.0 обусловлена использованием пакета mailtools;

3.0: перед анализом с помощью пакета email пакет mailtools декодирует байты
полного текста сообщения;
3.0: для отображения пакет mailtools декодирует основной текст,
commonhtml декодирует заголовки сообщения;
# ---------------------------------------------------------------------------- #
"""

import cgi
import commonhtml, secret
from externs import mailtools

# commonhtml.dumpstatepage(0)

def saveAttachments(message, parser, savedir='partsdownload'):
	"""
	сохраняет части полученного сообщения в файлы на сервере
	для дальнейшего просмотра в веб-браузере пользователя
	"""
	import os
	if not os.path.exists(savedir):								# CWD CGI-сценария на сервере
		os.mkdir(savedir)										# будет открываться в браузере
	for filename in os.listdir(savedir):						# удалить прежние файлы: временные!
		dirpath = os.path.join(savedir, filename)
		os.remove(dirpath)
	typesAndNames = parser.saveParts(savedir, message)
	filenames = [fname for (ctype, fname) in typesAndNames]
	for filename in filenames:
		os.chmod(filename, 0o666)								# некоторые серверы требуют права на чтение/запись
	return filenames

form = cgi.FieldStorage()
user, pswd, site = commonhtml.getstandardpopfields(form)
pswd = secret.decode(pswd)

try:
	msgnum = form['mnum'].value
	parser = mailtools.MailParser()
	fetcher = mailtools.SilentMailFetcher(site, user, pswd)
	fulltext = fetcher.lownloadMessage(int(msgnum))				# не используйте eval !
	message = parser.parseMessage(fulltext)						# Message в пакете email
	parts = saveAttachments(message, parser)					# для URL-ссылок
	mtype, content = parser.findMainText(message)				# первая текстовая часть
	commonhtml.viewpage(msgnum, message, content, form, parts)
except:
	commonhtml.errorpage('Error loading message')
#!/usr/local/bin/python3
#-*- coding: utf-8 -*-
# Глава 15. Сервер PyMailCGI.
# Вспомогательные модули.
# Общий вспомогательный модуль.
# Пример 16.14 (Лутц Т2 стр.656)
"""
# ---------------------------------------------------------------------------- #
Генерирует стандартный заголовок страницы, список и нижний колонтитул;
в этом файле скрыты детали, относящиеся к созданию разметки HTML;
выводимый здесь текст поступает клиенту через сокеты, создавая части
новой веб-страницы в веб-браузере; каждая строка выводится отдельным
вызовом print, использует urllib для экранирования параметров
в ссылках URL, создаваемых из словаря, а для вставки их в скрытые
поля форм HTML - cgi.escape (html.escape); некоторые инструменты отсюда могут
использоваться вне pymailcgi; можно было бы возвращать генерируемую
разметку HTML вместо вывода в поток, для включения в другие страницы;
можно было бы выстроить структуру в виде единого сценария CGI, который
получает и проверяет имя следующей операции в скрытом поле формы;
предупреждение: система действует, но была написана в основном во время
2-часовой задержки в чикагском аэропорту o'Hare: некоторые компоненты
стоило бы улучшить и оптимизировать;
# ---------------------------------------------------------------------------- #
"""

import cgi, urllib.parse, sys, os, html

# настройка трассировки исполнения сценария CGI
trace = True
a = (str(sys.stderr))
if trace:
	import time
	loggedpath = os.path.join(os.getcwd(), 'TraceLog')
	if not os.path.exists(loggedpath):
		os.mkdir(loggedpath)
	loggedfile = os.path.join(loggedpath, 'trace.log')
	sys.stderr = open(loggedfile, 'w', encoding='utf-8')
	print(file=sys.stderr)
	print('#'*60, file=sys.stderr)
	print(time.ctime(time.time()), file=sys.stderr)

# 3.0: в Python 3.1 наблюдаются проблемы при выводе некоторых
# декодированных строк str в поток вывода stdout
import builtins

bstdout = open(sys.stdout.fileno(), 'wb')

def print(*args, end='\n'):
	try:
		builtins.print(*args, end=end)
		sys.stdout.flush()
	except:
		for arg in args:
			bstdout.write(str(arg).encode('utf-8'))
		if end:
			bstdout.write(end.encode('utf-8'))
		bstdout.flush()

# FIXME комментировать временно
# sys.stderr = sys.stdout										# выводить сообщения об ошибках в браузер
from externs import mailconfig								# из пакета, находящегося на сервере
from externs import mailtools								# для анализа и дкодирования заголовков
parser = mailtools.MailParser()								# один парсер на процесс в этом модуле

# корневой каталог cgi-сценариев
# urlroot = 'http://starship.python.net/~lutz/PyMailCgi/'
# urlroot = 'http://localhost:8000/cgi-bin/'

urlroot = ''												# использовать минимальные относительные пути

def pageheader(app='PyMailCGI', color='#FFFFFF', kind='main', info=''):
	print('Content-type: text/html\n')
	print('<html lang="ru"><head><title>%s: %s page (PP4E)</title></head>' % (app, kind))
	print('<body bgcolor="%s"><h1>%s %s</h1><hr>' % (color, app, (info or kind)))

def pagefooter(root='pymailcgi.html'):
	print('</p><hr><a href="http://www.python.org">')
	print('<img src="../PythonPoweredSmall.gif" ')
	print('align="left" alt="[Python Logo]" border="0" hspace="15"</a>')
	print('<a href="../%s">Back to root page</a>' % root)
	print('</body></html>')

def formatlink(cgiurl, parmdict):
	"""
	создает ссылку запроса "%url?key=val&key=val" из словаря;
	экранирует str() всех ключей и значений, подставляя %xx,
	замещает ' ' на +
	обратите внимание, что адреса URL экранируются иначе, чем HTML
	(cgi.escape)
	"""
	parmtext = urllib.parse.urlencode(parmdict)				# вызовет parse.quote_plus
	return '%s?%s' % (cgiurl, parmtext)						# всю работу делает urllib

def pagelistsimple(linklist):								# выводит простой нумерованный список
	print('<ol>')
	for (text, cgiurl, parmdict) in linklist:
		link = formatlink(cgiurl, parmdict)
		text = html.escape(text)
		print('<li><a href="%s">\n %s</a></li>' % (link, text))
	print('</ol>')

def pagelisttable(linklist):								# выводит список в виде таблицы
	print('<p><table border>')								# для верности выполняет экранирование
	for (text, cgiurl, parmdict) in linklist:
		link = formatlink(cgiurl, parmdict)
		text = html.escape(text)
		tracelog1 = open('trace.log', 'a', encoding='utf-8')
		tracelog1.write('---> onViewPswdSubmit:')
		tracelog1.write('\t' + text)
		print('<tr><th><a href="%s">View</a></th><td>\n %s</td></tr>' % (link, text))
	print('</table>')

def listpage(linklist, kind='selection list'):
	pageheader(kind=kind)
	pagelisttable(linklist)									# [('text', 'cgiurl', {'parm': 'value'})]
	pagefooter()

def messagearea(headers, text, extra=''):					# extra - для readonly
	addrhdrs = ('From', 'To', 'Cc', 'Bcc')					# декодировать только имена
	print('<table border cellpadding="3">')
	for hdr in ('From', 'To', 'Cc', 'Subject'):
		rawhdr = headers.get(hdr, '?')
		if hdr in addrhdrs:
			dechdr = parser.decodeHeader(rawhdr)			# 3.0: декодировать для отображения
		else:												# закодированы при отправке
			dechdr = parser.decodeAddrHeader(rawhdr)		# только имена в адресах
		val = html.escape(dechdr, quote=1)
		print('<tr><th align="right">%s:' % hdr)
		print('    <td><input type="text" ')
		print('    name="%s" value="%s" %s size="60">' % (hdr, val, extra))
		print('<tr><th align="right">Text:')
		print('<td><textarea name="text" cols="80" rows="10" %s' % extra)
		print('%s\n</textarea></table>' % (html.escape(text) or '?'))

def viewattachmentlinks(partnames):
	"""
	создает гиперссылки для сохраненных локально файлов частей/вложений,
	открытие файлов будет выполнять веб-браузер
	предполагается наличие единственного пользователя, файлы сохраняются
	только для одного сообщения
	"""
	print('<hr><table border cellpadiing="3"><tr><th>Parts:')
	for filename in partnames:
		basename = os.path.basename(filename)
		filename = filename.replace('\\', '/')				# грубый прием для Windows
		print('<td><a href="../%s>%s</a>' % (filename, basename))
	print('</table><hr>')

def viewpage(msgnum, headers, text, form, parts=[]):
	"""
	при выборе сообщения в списке и выполнении операции просмотра
	(вызывается щелчком на созданной ссылке)
	очень тонкое место: к этому моменту пароль был закодирован в ссылке,
	в формате URL, и затем декодировался при анализе входных данных;
	здесь он встроен в разметку HTML, поэтому мы применяем cgi.escape;
	обычно в скрытых полях появляются непечатные символы,
	но в IE и NS как-то работает:
	в url: ?user=lutz&mnum=3&pswd=%8cg%c2P%1e%f0%5b%c5J%1c%f3&...
	в html: <input type=hidden name=pswd value="...непечатные...">
	можно бы пропустить поле HTML через urllib.parse.quote,
	но это потребовало бы вызывать urllib.parse.unquote в следующем
	сценарии (что не мешает передавать данные в URL, а не в форме);
	можно верняться к цифровому формату строк из secret.py
	"""
	pageheader(kind='View')
	user, pswd, site = list(map(html.escape, getstandardpopfields(form)))
	print('<form method="post" action="%sonViewPageAction.py">' % urlroot)
	print('<input type="hidden" name="mnum" value="%s">' % msgnum)
	print('<input type="hidden" name="user" value="%s">' % user)
	print('<input type="hidden" name="site" value="%s">' % site)
	print('<input type="hidden" name="pswd" value="%s">' % pswd)
	messagearea(headers, text, 'readonly')
	if parts:
		viewattachmentlinks(parts)

	# onViewPageAction.quotetext требует передачи даты в странице
	print('<input type="hidden" name="Date" value="%s">' % headers.get('Date', '?'))
	print('<table><tr><th align="right">Action:')
	print('<td><select name="action">')
	print('    <option>Reply<option>Forward<option>Delete</select>')
	print('<input type="submit" value="Next">')
	print('</table></form>')
	pagefooter()

def sendattachmentwidgets(maxattach=3):
	print('<p><b>Attach:</b><br>')
	for i in range(1, maxattach+1):
		print('<input size="80" type="file" name="attach%d"><br>' % i)
	print('</p>')

def editpage(kind, headers={}, text=''):
	# вызывается при отправке, View+выбор+Reply, View+выбор+Fwd
	pageheader(kind=kind)
	print('<p><form enctype="multipart/form-data" method="post"', end=' ')
	print('action="%sonEditPageSend.py">' % urlroot)
	if mailconfig.mysgnature:
		text = '\n%s\n%s' % (mailconfig.mysgnature, text)
	messagearea(headers, text)
	sendattachmentwidgets()
	print('<input type="submit" value="Send">')
	print('<input type="reset" value="Reset">')
	print('</form>')
	pagefooter()

def errorpage(message, stacktrace=True):
	pageheader(kind='Error')
	exc_type, exc_value, exc_tb = sys.exc_info()
	print('<h2>Error Description</h2><p>', message)
	print('<h2>Python Exception</h2><p>', html.escape(str(exc_type)))
	print('<h2>Exception details</h2><p>', html.escape(str(exc_value)))
	if stacktrace:
		print('<h2>Exception traceback</h2><p><pre>')
		import traceback
		traceback.print_tb(exc_tb, None, sys.stdout)
		print('</pre>')
	pagefooter()

def confirmationpage(kind):
	pageheader(kind='Confirmation')
	print('<h2>%s operation was successful</h2>' % kind)
	print('<p>Press the link below to retirn to the main page.</p>')
	pagefooter()

def getfield(form, field, default=''):
	# имитация метода get словаря
	return (field in form and form[field].value) or default

def getstandardpopfields(form):
	"""
	поля могут отсутствовать, быть пустыми или содержать значение,
	жестко определены в URL; по умолчанию используются настройки из mailconfig
	"""
	return (getfield(form, 'user', mailconfig.popusername),
			getfield(form, 'pswd', '?'),
			getfield(form, 'site', mailconfig.popservername))

def getstandardsmtpfields(form):
	return getfield(form, 'site', mailconfig.smtpservername)

def runsilent(func, args):
	"""
	выполняет функцию, подавляя вывод в stdout
	например: подавляет вывод из импортируемых инструментов,
	чтобы он не попал клиенту/браузеру
	"""
	class Silent:
		def write(self, line): pass
	save_stdout = sys.stdout
	sys.stdout = Silent()									# отправлять вывод в фиктивный объект,
	try:													# который имеет метод write
		result = func(*args)								# попытаться вернуть результат функции
	finally:												# и всегда восстанавливать stdout
		sys.stdout = save_stdout
	return result

def dumpstatepage(exhaustive=0):
	"""
	для отладки: вызывается в начале сценарий CGI
	для создания новой страницы с информацией о состоянии CGI
	"""
	if exhaustive:
		cgi.test()											# вывести страницу с формой, окружностью и проч.
	else:
		pageheader(kind='state dump')
		form = cgi.FieldStorage()							# вывести только имена/значения полей формы
		cgi.print_form(form)
		pagefooter()
	sys.exit()

def selftest(showastable=False):							# создает фиктивную веб-страницу
	links = [
		('text1', urlroot + 'page1.cgi', {'a': 1}),
		('text2', urlroot + 'page1.cgi', {'a': 2, 'b': 3}),
		('text3', urlroot + 'page2.cgi', {'x': 'a b', 'y': 'a<b&c', 'z': '?'}),
		('text4', urlroot + 'page2.cgi', {'<x>': '', 'y': '<a>', 'z': None})
	]
	pageheader(kind='Test')
	if showastable:
		pagelisttable(links)
	else:
		pagelistsimple(links)
	pagefooter()


if __name__ == "__main__":
	selftest(len(sys.argv) > 1)								# разметка HTML выводится в stdout

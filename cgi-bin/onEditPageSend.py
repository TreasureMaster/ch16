#!/usr/local/bin/python3
#-*- coding: utf-8 -*-
# Глава 15. Сервер PyMailCGI.
# Отправка почты по SMTP.
# Сценарий отправки почты.
# Пример 16.4 (Лутц Т2 стр.604)
"""
# ---------------------------------------------------------------------------- #
Вызывается при отправке формы в окне редактирования: завершает составление
нового сообщения, ответа или пересылаемого сообщения;

В 2.0+: мы повторно используем инструменты из пакета mailtools
для конструирования и отправки сообщения вместо устаревшей схемы, основанной
на строковых методах; из этого модуля мы также наследуем возможность
добавлять вложения и преобразовывать отправляемые сообщения в формат MIME;

3.0: выгрузка через CGI двоичных вложений и текстовых вложений
в несовместимой кодировке не допускается из-за ограничения модуля cgi
в Py3.1, поэтому мы просто используем здесь кодировку по умолчанию
для данной платформы (механизм синтаксического анализа, используемый
модулем cgi, не может предложить ничего лучше);
3.0: кроме того, для основого текста и для вложений используются
простые правила кодирования Юникода;
# ---------------------------------------------------------------------------- #
"""

import cgi, sys, commonhtml, os
from externs import mailtools

savedir = 'partsupload'
if not os.path.exists(savedir):
	os.mkdir(savedir)

def saveAttachments(form, maxattach=3, savedir=savedir):
	"""
	сохраняет выгруженные файлы вложений в локальных файлах на сервере,
	откуда mailtools будет добавлять их в сообщение; класс FieldStorage
	в 3.1 и другие компоненты модуля cgi могут вызывать появление ошибки
	для многих типов выгружаемых файлов, поэтому мы не будем прилагать
	особых усилий, чтобы попытаться определить корректную
	кодировку символов;
	"""
	partnames = []
	for i in range(1, maxattach+1):
		fieldname = 'attach%d' % i
		if fieldname in form[fieldname].filename:
			fileinfo = form[fieldname]							# передана и заполнена?
			filedata = fileinfo.value							# прочитать в строку
			filename = fileinfo.filename						# путь на стороне клиента
			if '\\' in filename:
				basename = filename.split('\\')[-1]				# для клиентов DOS
			else:
				basename = filename.split('/')[-1]				# для клиентов Unix
			pathname = os.path.join(savedir, basename)
			if isinstance(filedata, str):						# 3.0: rb требует bytes
				filedata = filedata.encode()					# 3.0: использовать кодировку?
			savefile = open(pathname, 'wb')
			savefile.write(filedata)							# или с инструментом with
			savefile.close()									# но EIBTI
			os.chmod(pathname, 0o666)							# требуется некоторыми серверами
			partnames.append(pathname)							# список локальных путей
	return partnames											# определить тип по имени

# commonhtml.dumpstatepage(0)
form = cgi.FieldStorage()
attaches = saveAttachments(form)								# cgi.print_form(form), чтобы посмотреть

# имя сервера из модуля или из URL, полученного методом GET
smtpservername = commonhtml.getstandardsmtpfields(form)

# здесь предполагается, что параметры получены из формы или из URL
from commonhtml import getfield									# для получения значений атрибутов
From = getfield(form, 'Form')									# пустые поля не должны отправляться
To = getfield(form, 'To')
Cc = getfield(form, 'Cc')
Subj = getfield(form, 'Subject')
text = getfield(form, 'text')
if Cc == '?': Cc = ''

# 3.0: не-ascii заголовки кодируются в utf8 в пакете mailtools
parser = mailtools.MailParser()
Tos = parser.splitAddresses(To)									# списки получателей: разделитель ','
Ccs = (Cc and parser.splitAddresses(Cc)) or ''
extraHdrs = [('Cc', Ccs), ('X-Mailer', 'PyMailCGI 3.0')]

# 3.0: определить кодировку для основного текста и текстовых вложений;
# по умолчанию = ascii в mailtools
bodyencoding = 'ascii'
try:
	text.encode(bodyencoding)									# сначала попробовать ascii (или latin-1 ?)
except (UnicodeError, LookupError):								# иначе использовать utf8 (или из настроек ?)
	bodyencoding = 'utf-8'										# что сделать: это более ограниченное решение, чем в PyMailGUI

# 3.0: использовать utf8 для всех вложений;
# здесь мы не можем спросить у пользователя
attachencodings = ['utf-8'] * len(attaches)						# игнорировать нетекстовые части

# кодировать и отправить
sender = mailtools.SilentMailSender(smtpservername)

try:
	sender.sendMessage(From, Tos, Subj, extraHdrs, text, attaches,
					   bodytextEncoding=bodyencoding,
					   attachesEncodings=attachencodings)
except:
	commonhtml.errorpage('Send mail error')
else:
	commonhtml.confirmationpage('Send mail')
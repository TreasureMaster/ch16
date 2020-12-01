#!/usr/local/bin/python3
#-*- coding: utf-8 -*-
# Глава 15. Сервер PyMailCGI.
# Вспомогательные модули.
# Внешние компоненты и настройки.
# Пример 16.11 (Лутц Т2 стр.644)
"""
# ---------------------------------------------------------------------------- #
Пользовательские настройки для различных почтовых программ
(версия для PyMailCGI);
Сценарии для работы с электронной почтой получают имена серверов и другие
параметры из этого модуля: измените модуль так, чтобы он отражал имена
ваших серверов, вашу подпись и предпочтение;
# ---------------------------------------------------------------------------- #
"""

# from Tom2.ch14.myconfig import * 				# использовать настройки из главы 13
from Tom2.ch13.mailtools.resolvingConfig import mailconfig

fetchlimit = 50									# 4E: максимальное число загружаемых заголовков/сообщений
												# (по умолчанию = 25)


if __name__ == "__main__":
	import sys
	print(dir(mailconfig))
	# print(dir(__name__))
	for attr in dir(mailconfig):
		if not attr.startswith('__'):
			# print(attr, '=>', getattr(mailconfig, attr))
			setattr(sys.modules[__name__], attr, getattr(mailconfig, attr))
	print(smtpuser)
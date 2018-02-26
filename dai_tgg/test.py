# -*- coding: utf-8 -*-
import datetime
a = datetime.datetime.now().strftime('%d-%m-%Y 00:00')
b = datetime.datetime.strptime(a, '%d-%m-%Y 00:00')
print (b)
# print (datetime.datetime.now().strftime('%d-%m-YY') + datetime.timedelta(hours=1))

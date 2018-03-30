# -*- coding: utf-8 -*-
import re
a=u'''
Spares High End including Server tứ  
'''
print re.sub('^\S*\s','',a)
b = a.strip()
print b
print a
print 'chót'
# -*- coding: utf-8 -*-
import string
import datetime
from dateutil.relativedelta import relativedelta
import pytz
# print u'%s'%str(tuple([1]))
a = {1:3}
print a.get(2)
# class A():
#     b = 1
#     def a(self):
#         self.b = 2
#         
# a = A()
# print A.__dict__
# print 'ir_sequence_%03d' % 29
# x = 4433.2
# print '{0:,.0f}'.format(x)
# print '{0:.2f}'.format(x)
# print '{:06.2f}'.format(3.141592653589793)

# print 3 ==3.0

# from mytools import convert_utc_to_gmt_7
# def decorator(f):
#     print 'out wrapper'
#     def wrapper(x):
#         print 'in wrapper'
#         f(x)
#     return wrapper
# a = 0
# class A():
#     def __init__(self,a):
#         self.a=1
# #     @decorator
#     def f(self):
#         print 'hehe'
#     f = decorator(f)
#     def f1(self):
#         self.f()
#         
#          
#     
# 
# i =A(1)
# i.f()
# a = [1,2,1]
# for c,i in enumerate(a):
#     b = a.index(i)
#     print c,b
# a = {1:3}
# print a.get(3,False)

# import re
# string = u'    anh             con    no em '
# def viet_tat(string):
#     string = string.strip()
#     ns = re.sub('\s{2,}', ' ', string)
#     rs = ns.split(' ')
#     rs = map(lambda word: word[0],rs)
#     rs = ''.join(rs).upper()
#     return rs
# rs = viet_tat(string)
# print rs

# string = u'...---===+++***&&&^^^%%$$$##@@!Tăng cường xử lý ứng cứu (tùy thực tế)'
# ns = re.sub('[^\w ]','', string,flags = re.UNICODE)
# print ns

# print [ f 
#        for f in range(5) 
#        if f %2]
# 
# for i in range(0,10):
#     for j in range (0,10):
#         i = i + 1
#         print i

# from collections import deque
# print deque()
# l = [1,2,3]
# # l = deque(l)
# # l.popleft()
# # print l
# i= 5
# for i in l:
#     break
# print i

# num2alpha = dict(zip(range(0, 26), string.ascii_uppercase))
# 
# print num2alpha

# adict = {'a':1}
# print u' %(a)s noi di %(a)s'%adict
# vn_time = datetime.datetime.now()
# vn_time= datetime.datetime(2011, 1, 3, 20, 0)
# print vn_time
# # vn_time = convert_utc_to_gmt_7(utc_time)
# vn_time = vn_time + relativedelta(month=1)
# str_dau_thang = vn_time.strftime('%Y-%m-%d')
# print str_dau_thang
# str = 'anh yeu  em'
# array  = str.split(' ')
# print array
# import re
# rs = re.findall('(\W+)', 'Words, words, words.')
# print rs
# rs = re.split('(\W+)', 'Words, words, words.')
# print rs




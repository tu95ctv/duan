# -*- coding: utf-8 -*-

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

import re
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

string = u'...---===+++***&&&^^^%%$$$##@@!Tăng cường xử lý ứng cứu (tùy thực tế)'
ns = re.sub('[^\w ]','', string,flags = re.UNICODE)
print ns








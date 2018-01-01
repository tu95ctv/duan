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
a = [1,2,1]
for c,i in enumerate(a):
    b = a.index(i)
    print c,b
    

 # -*- coding: utf-8 -*-
import re
import xlrd
import time
import datetime
from odoo.exceptions import UserError
from odoo import  fields
import base64
from copy import deepcopy
import logging
_logger = logging.getLogger(__name__)
from odoo.osv import expression


def get_or_create_object_sosanh(self,class_name,search_dict,
                                create_write_dict ={},is_must_update=False,noti_dict=None,
                                not_active_include_search = False,model_effect_noti_dict=False):
    #print 'in get_or create fnc','search_dict',search_dict,'create_write_dict',create_write_dict
    global log_new
    if not_active_include_search:
        domain_not_active = ['|',('active','=',True),('active','=',False)]
    else:
        domain_not_active = []
#     domain_list =  domain_not_active
    domain = []
    if noti_dict =={}:
        noti_dict['create'] = 0
        noti_dict['update'] = 0
        noti_dict['skipupdate'] = 0
    for i in search_dict:
        tuple_in = (i,'=',search_dict[i])
        domain.append(tuple_in)
    domain = expression.AND([domain_not_active, domain])
    searched_object  = self.env[class_name].search(domain)
    if not searched_object:
        search_dict.update(create_write_dict)
        created_object = self.env[class_name].create(search_dict)
        if noti_dict !=None and ( model_effect_noti_dict==False or model_effect_noti_dict==class_name):
            noti_dict['create'] = noti_dict.get('create',0) + 1
        return_obj =  created_object
    else:
        if not is_must_update:
            is_write = False
            for attr in create_write_dict:
                domain_val = create_write_dict[attr]
                exit_val = getattr(searched_object,attr)
                try:
                    exit_val = getattr(exit_val,'id',exit_val)
                    if exit_val ==None: #recorderset.id ==None when recorder sset = ()
                        exit_val=False
                except:#singelton
                    pass
                if isinstance(domain_val, datetime.date):
                    exit_val = fields.Date.from_string(exit_val)
                if exit_val !=domain_val:
                    #print 'exit_val','domain_val',exit_val,domain_val
                    is_write = True
                    break
            
        else:
            is_write = True
        if is_write:
            searched_object.sudo().write(create_write_dict)
            if noti_dict !=None and ( model_effect_noti_dict==False or model_effect_noti_dict==class_name):
                noti_dict['update'] = noti_dict.get('update',0) + 1
            #print 'searched_object 2'

        else:#'update'
            if noti_dict !=None and ( model_effect_noti_dict==False or model_effect_noti_dict==class_name):
                noti_dict['skipupdate'] = noti_dict.get('skipupdate',0) + 1
                log_new += search_dict['name'] + '\n'

        #print 'is_write***',is_write,'class_name',class_name,'noti_dict',noti_dict
        return_obj = searched_object
    #print 'domain_list 2',domain_list
    return return_obj
    
EMPTY_CHAR = [u'',u' ',u'\xa0']
def check_variable_is_not_empty_string(readed_xl_value):
    if  isinstance(readed_xl_value,unicode) or isinstance(readed_xl_value,str) :
        if readed_xl_value  in EMPTY_CHAR:
            return False
        rs = re.search('\S',readed_xl_value)
        if not rs:
            return False
    return True        
  
def print_diem(val):
    #print 'diem',val,type(val)
    return val
def ham_tao_tvcvlines():
    pass
INVALIDS = ['No serial','N/A','NA','--','-','BUILTIN','0','1']
#INVALIDS=map(lambda i:i.lower(),INVALIDS)
def valid_sn_pn(sn_pn):
    if isinstance(sn_pn, unicode):
        if sn_pn in INVALIDS:
            return False
    return sn_pn
        #sn_pn = sn_pn.lower()
def sn_bi_false(sn_pn):
    if isinstance(sn_pn, unicode):
        if sn_pn in INVALIDS:
            return sn_pn
    return False

def sn_map(val):
    rs = re.findall('Serial number.*?(\w+)',val)
    if rs:
        return rs[0]
def import_strect(odoo_or_self_of_wizard):
    self = odoo_or_self_of_wizard
    for r in self:
            noti_dict = {}
            recordlist = base64.decodestring(r.file)
            xl_workbook = xlrd.open_workbook(file_contents = recordlist)
            begin_row_offset = 0
            if r.type_choose==u'640':
                sheet_names = xl_workbook.sheet_names()
                #sheet_names = ['VTN-137P-4-2']
            for sheet_name in sheet_names:
                sheet = xl_workbook.sheet_by_name(sheet_name)
                if r.type_choose ==u'640':
                    model_name = 'kknoc'
                    field_dict= (
                            ('sn',{'func':sn_map,'contain':u'Serial number','key':'Both','col_index':7}),
                            
#                             ('stt',{'func':None,'xl_title':u'stt','key':True}),
#                             ('so_the',{'func':None,'xl_title':u'Số thẻ','key':True}),
#                             ('pn',{'func':valid_sn_pn,'xl_title':u'Part-Number','key':True}),
#                             ('pn_id',{'model':'pn','func':valid_sn_pn,'xl_title':u'Part-Number','key':False}),
#                             ('sn_false',{'func':sn_bi_false,'xl_title':None,'key':False,'col_index':7}),
                            
                            )
                column_number = 0
                key_search_dict = {}
                update_dict = {}
                data=''
                for row in range(begin_row_offset,sheet.nrows):
                        #print 'row',row
                        read_value = sheet.cell_value(row,column_number)
                        if read_value:
                            if read_value:
                                data = data + '\n' + read_value
                            for field,field_attr in field_dict:
                                func = field_attr['func']
                                val = func (read_value)
                                if val != None:
                                    if field_attr['key']==True:
                                        key_search_dict[field] = val
                                    elif  field_attr['key']=='Both':
                                        key_search_dict[field] = val
                                        update_dict[field] = val
                                    else:
                                        update_dict[field] = val
                                    break
                        else:
                            if key_search_dict:
                                update_dict['sheet_name'] = sheet_name
                                update_dict['file_name'] = r.type_choose
                                update_dict['data'] = data
                                get_or_create_object_sosanh(self,model_name,key_search_dict,update_dict,True,noti_dict=noti_dict )
                                key_search_dict = {}
                                update_dict = {}
                                data = ''
                    
                     
                    
                 
            r.create_number = noti_dict['create']
            r.update_number = noti_dict['update']
            r.skipupdate_number = noti_dict['skipupdate']
# def func_for_skip_cell (val):
#     if len(val)< 2:
#         return True
#     else:
#         return False
        
log = u''
def write_log(val):
    pass
def ham_tao_tv_con(self_,val,field_attr,key_search_dict,update_dict,noti_dict):
    alist = val.split(',')
    alist = filter(check_variable_is_not_empty_string,alist)
    len_alist = len(alist)
    diem_percent = 100/len(alist)
    key_name = field_attr.get('key_name','name')
    parent_id_name = key_search_dict['name']
    def tao_thu_vien_childrens(val):
        i = val[0]
        val = val[1]
        val = val.strip().capitalize()
        name_tv_con = val  # + u'|Công Việc Cha: '  + key_search_dict['name']
        parent_id = get_or_create_object_sosanh (self_,'tvcv',{'name':parent_id_name},noti_dict=noti_dict)
        if i ==len_alist-1:
            diem_percent_l =100- (len_alist-1)*diem_percent
        else:
            diem_percent_l = diem_percent
            
        return get_or_create_object_sosanh(self_,field_attr['model'],{key_name:name_tv_con,'parent_id':parent_id.id},{'diem_percent':diem_percent_l,
                                                                                                                     'don_vi':update_dict['don_vi'],
                                                                                                                     'cong_viec_cate_id':update_dict['cong_viec_cate_id'],
                                                                                                                     'parent_id':parent_id.id,
                                                                                                                     'loai_record':u'Công Việc'
                                                                                                                     } )
    a_object_list = map(tao_thu_vien_childrens,enumerate(alist))
    a_object_list = map(lambda x:x.id,a_object_list)
    val = [(6, False, a_object_list)]
    return val
def active_function(val):
    return False if val ==u'na' else True

def read_merge_cell(sheet,row,col,merge_tuple_list):
    for crange in merge_tuple_list:
        rlo, rhi, clo, chi = crange
        if row>=rlo and row < rhi and col >=clo and col < chi:
            row = rlo
            col = clo
            break
    val = sheet.cell_value(row,col)
    return val
def importthuvien(odoo_or_self_of_wizard):
    global log_new
    log_new = u''
    self = odoo_or_self_of_wizard
    for r in self:
            noti_dict = {}
            recordlist = base64.decodestring(r.file)
            xl_workbook = xlrd.open_workbook(file_contents = recordlist)
            begin_row_offset = 1
            not_active_include_search  =False
            loop_list = ['main']
            search_update_dict = {}
            if r.type_choose =='stock.inventory.line':
                sheet_names = [u'Truyền dẫn']
                model_name = 'stock.inventory.line'
                def chon_location_id(val):
                    location_id = xcel_data_of_a_row['location_id3'] or xcel_data_of_a_row['location_id2'] or xcel_data_of_a_row['location_id1'] or xcel_data_of_a_row['location_id_goc']
                    return location_id
#                 field_dict= (
#                          ('inventory_id', {'val':1,'key':False}),  
#                          ('location_id_goc', {'val':self.env['stock.location'].search([('name','=','LTK Dự Phòng')]).id,'key':False,'for_excel_readonly':True}),                       
#                          ('location_id1', {'model':'stock.location','for_excel_readonly':True,
#                                             'fields':[
#                                                 ('name',{'func':None,'xl_title':u'Phòng','key':True})
#                                                 ('location_id',{'func':lambda val: xcel_data_of_a_row['location_id_goc'],'key':True})
#                                                 ]
#                                            }),    
#                          
#                          ('location_id1', {'model':'stock.location','func':None,'xl_title':u'Phòng','key':False,'for_excel_readonly':True, 'more_fields':[('location_id',{'func':lambda val: xcel_data_of_a_row['location_id_goc'],'key':True})]   }),    
#                          ('location_id2', {'model':'stock.location','func':None,'xl_title':u'Tủ/Kệ','key':False,'for_excel_readonly':True,'more_fields':[('location_id',{'func':lambda val: xcel_data_of_a_row['location_id1'] or xcel_data_of_a_row['location_id_goc'] ,'key':True})]}), 
#                          ('location_id3', {'model':'stock.location','func':None,'xl_title':u'Ngăn','key':False,'for_excel_readonly':True,'more_fields':[('location_id',{'func':lambda val: xcel_data_of_a_row['location_id2'] or xcel_data_of_a_row['location_id1'] or xcel_data_of_a_row['location_id_goc'],'key':True})]}), 
#                          ('location_id', {'val':'Cheat Code', 'func':chon_location_id, 'key':False}),                    
#                          ('tinh_trang', {'func':None,'xl_title':u'Tình trạng','key':False,'for_excel_readonly':True,'break_when_xl_field_empty':True}),                       
#                          ('prod_lot_id_only_read_excel', {'xl_title':u'Seri Number','for_excel_readonly':True}),
#                          ('product_id', {'func':None,'xl_title':u'TÊN VẬT TƯ','key':True,'more_fields':[('tracking',{'func':lambda val: 'serial' if xcel_data_of_a_row['prod_lot_id_only_read_excel'] !=False else 'none' }),('type',{'val':'product'})]}),
#                         ('prod_lot_id', {'key':True,
#                                           'fields':[
#                                               ('name',{'func':lambda val: int(val) if isinstance(val,float) else val,'xl_title':u'Seri Number','key':True})
# #                                               ('product_id',{'func':lambda val: search_update_dict['product_id'] })
#                                                 ('product_id',{'fields':('name',{'func':None,'xl_title':u'TÊN VẬT TƯ',})
#                                                                })
# 
#                                               ]
#                                           }),
#                         
#                          
#                          ('product_qty', {'func':lambda val: 1 if  (search_update_dict['prod_lot_id'] and val > 1) else val ,'xl_title':u'Tồn kho cuối kỳ','key':False }),
#                          #('name', {'func':None,'xl_title':u'Seri Number','key':True,'break_when_xl_field_empty':True }),
#                          )
                field_dict= [
#                          ('inventory_id', {'val':1,'key':False}),  
#                          ('location_id_goc', {'val':self.env['stock.location'].search([('name','=','LTK Dự Phòng')]).id,'key':False,'for_excel_readonly':True}),                       
#                          ('location_id1', {'model':'stock.location','for_excel_readonly':True,
#                                             'fields':[
#                                                 ('name',{'func':None,'xl_title':u'Phòng','key':True})
#                                                 ('location_id',{'func':lambda val: xcel_data_of_a_row['location_id_goc'],'key':True})
#                                                 ]
#                                            }),    
#                          
#                          ('location_id1', {'model':'stock.location','func':None,'xl_title':u'Phòng','key':False,'for_excel_readonly':True, 'more_fields':[('location_id',{'func':lambda val: xcel_data_of_a_row['location_id_goc'],'key':True})]   }),    
#                          ('location_id2', {'model':'stock.location','func':None,'xl_title':u'Tủ/Kệ','key':False,'for_excel_readonly':True,'more_fields':[('location_id',{'func':lambda val: xcel_data_of_a_row['location_id1'] or xcel_data_of_a_row['location_id_goc'] ,'key':True})]}), 
#                          ('location_id3', {'model':'stock.location','func':None,'xl_title':u'Ngăn','key':False,'for_excel_readonly':True,'more_fields':[('location_id',{'func':lambda val: xcel_data_of_a_row['location_id2'] or xcel_data_of_a_row['location_id1'] or xcel_data_of_a_row['location_id_goc'],'key':True})]}), 
#                          ('location_id', {'val':'Cheat Code', 'func':chon_location_id, 'key':False}),                    
#                          ('tinh_trang', {'func':None,'xl_title':u'Tình trạng','key':False,'for_excel_readonly':True,'break_when_xl_field_empty':True}),                       
#                          ('prod_lot_id_only_read_excel', {'xl_title':u'Seri Number','for_excel_readonly':True}),
#                          ('product_id', {'key':True,
#                                          'fields':[
#                                              ('name',{'func':None, 'xl_title':u'TÊN VẬT TƯ','key': True}),
#                                              ('tracking',{'func':lambda val: 'serial' if xcel_data_of_a_row['prod_lot_id_only_read_excel'] !=False else 'none' }),
#                                              ('type',{'val':'product'})]
#                                          }),
#                          
#                          
                         ('prod_lot_id', {'key':True,
                                          'fields':[
                                            ('name',{'func':lambda val: int(val) if isinstance(val,float) else val,'xl_title':u'Seri Number','key':True}),
#                                               ('product_id',{'func':lambda val: search_update_dict['product_id'] })
                                            ('product_id',{'fields':[
                                                ('name',{'func':None,'xl_title':u'TÊN VẬT TƯ',}),
                                                ],'key':False}),
                                                    
                                              ]
                                          }),
                        
                         
#                          ('product_qty', {'func':lambda val: 1 if  (search_update_dict['prod_lot_id'] and val > 1) else val ,'xl_title':u'Tồn kho cuối kỳ','key':False }),
                         ]
                
                MODEL_DICT = {'model':model_name,'fields':field_dict}
                title_rows = [4,5]
                begin_row_offset = 3
           
            ### Xong khai bao
            def recursive_read_field_attr(MODEL_DICT):
                model_name = MODEL_DICT['model']
                fields= self.env[model_name]._fields
                for field_tuple in MODEL_DICT['fields']:
                    f_name = field_tuple[0]
                    field_attr = field_tuple[1]
                    
                    if not field_attr.get('for_excel_readonly'):
                        field = fields[f_name]
                        if field.type =='many2many' or field.type == 'one2many':
                            field_attr['m2m'] = True
                        if field.comodel_name:
#                             print '**MODEL_DICT**',MODEL_DICT
#                             print '****comodel_name***',field.comodel_name
                            field_attr['model'] = field.comodel_name
                            recursive_read_field_attr(field_attr)
            def recursive_add_xl_column_attr(MODEL_DICT,row_title_index):
                print 'value_may_be_title',value_may_be_title
                model_name = MODEL_DICT['model']
                for field,field_attr in MODEL_DICT['fields']:
                    if field_attr.get('val',None) != None:
                        continue
                    if field_attr.get('xl_title') ==None and field_attr.get('col_index') !=None:
                        continue# cos col_index
                    elif field_attr.get('xl_title'):
                        if isinstance(field_attr['xl_title'],unicode) or  isinstance(field_attr['xl_title'],str):
                            xl_title_s = [field_attr['xl_title']]
                        else:
                            xl_title_s =  field_attr['xl_title']
                        for xl_title in xl_title_s:
                            if xl_title == value_may_be_title:
                                field_attr['col_index'] = col
                                if row_title_index ==None or  row > row_title_index:
                                    row_title_index = row
                                break
                    elif field_attr.get('fields'):
                        recursive_add_xl_column_attr (field_attr,row_title_index)
                                       
                    
            recursive_read_field_attr(MODEL_DICT)
#             print '***kq cuoi cung***',MODEL_DICT
#             self.log = MODEL_DICT
#             return False
            
#             fields= self.env[model_name]._fields
#             
#             for field_tuple in field_dict:
#                 f_name = field_tuple[0]
#                 field_attr = field_tuple[1]
#                 if not field_attr.get('for_excel_readonly'):
#                     field = fields[f_name]
#                     if field.comodel_name:
#                         field_attr['model'] = field.comodel_name
#                     if field.type =='many2many' or field.type == 'one2many':
#                         field_attr['m2m'] = True
                    

            for loop_instance in loop_list:
                for sheet_name in sheet_names:
                    sheet = xl_workbook.sheet_by_name(sheet_name)
                    row_title_index =None
                    for row in title_rows:
                        for col in range(0,sheet.ncols):
                            try:
                                value_may_be_title = unicode(sheet.cell_value(row,col))
                            except Exception as e:
                                raise ValueError(str(e),'row',row,'col',col,sheet_name)
                            recursive_add_xl_column_attr(MODEL_DICT,row_title_index)
                    self.log = MODEL_DICT
                    return False
#                             for field,field_attr in field_dict:
#                                 if field_attr.get('val',None) != None:
#                                     continue
#                                 if field_attr['xl_title'] ==None and field_attr['col_index'] !=None:
#                                     continue# cos col_index
#                                 if isinstance(field_attr['xl_title'],unicode) or  isinstance(field_attr['xl_title'],str):
#                                     xl_title_s = [field_attr['xl_title']]
#                                 else:
#                                     xl_title_s =  field_attr['xl_title']
#                                 for xl_title in xl_title_s:
#                                     if xl_title == value_may_be_title:
#                                         field_attr['col_index'] = col
#                                         if row_title_index ==None or  row > row_title_index:
#                                             row_title_index = row
#                                         break
                    
                    merge_tuple_list =  sheet.merged_cells
                    for c,row in enumerate(range(row_title_index+begin_row_offset,sheet.nrows)):
                        print 'count row',row
                        search_update_dict = {}
                        key_search_dict = {}
                        update_dict = {}
                        xcel_data_of_a_row = {}
                        len_field_dict = len(field_dict)
                        count = 0
                        for field,field_attr in field_dict:
                            count +=1
                            
                            noti_dict['break_when_xl_field_empty'] = noti_dict.setdefault('break_when_xl_field_empty',0) + 1
                            continue
                        if key_search_dict:
                                get_or_create_object_sosanh(self,model_name,key_search_dict,update_dict,is_must_update=True,noti_dict=noti_dict,not_active_include_search  =not_active_include_search)
                        else:
                            noti_dict['not_key_search_dict'] = noti_dict.setdefault('not_key_search_dict',0) + 1
                        
            r.create_number = noti_dict.get('create')
            r.update_number = noti_dict.get('update')
            r.skipupdate_number = noti_dict.get('skipupdate')
            r.log= noti_dict
            

            
            

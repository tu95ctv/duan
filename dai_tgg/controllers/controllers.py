# -*- coding: utf-8 -*-
from odoo import http
from openerp import http
from openerp.http import request
from openerp.addons.web.controllers.main import serialize_exception,content_disposition
import base64
# from openpyxl import load_workbook
from cStringIO import StringIO
from odoo.tools.misc import xlwt
from copy import deepcopy
from odoo import api,fields
import datetime
import odoo.addons.web.controllers.pivot as pivot
import json
from odoo.tools import ustr
from collections import deque
# from tools import convert_odoo_datetime_to_vn_str
from odoo.osv import expression

import pytz
import string


def convert_utc_to_gmt_7(utc_datetime_inputs):
    local = pytz.timezone('Etc/GMT-7')
    utc_tz =pytz.utc
    gio_bat_dau_utc_native = utc_datetime_inputs#fields.Datetime.from_string(self.gio_bat_dau)
    gio_bat_dau_utc = utc_tz.localize(gio_bat_dau_utc_native, is_dst=None)
    gio_bat_dau_vn = gio_bat_dau_utc.astimezone (local)
    return gio_bat_dau_vn
def convert_odoo_datetime_to_vn_datetime(odoo_datetime):
        utc_datetime_inputs = fields.Datetime.from_string(odoo_datetime)
        vn_time = convert_utc_to_gmt_7(utc_datetime_inputs)
        return vn_time
  
def convert_vn_datetime_to_utc_datetime(native_ca_gio_in_vn):
            local = pytz.timezone('Etc/GMT-7')
            utc_tz =pytz.utc
            gio_bat_dau_in_vn = local.localize(native_ca_gio_in_vn, is_dst=None)
            gio_bat_dau_in_utc = gio_bat_dau_in_vn.astimezone (utc_tz)
            return gio_bat_dau_in_utc
        
def convert_odoo_datetime_to_vn_str(odoo_datetime):
    if odoo_datetime:
        utc_datetime_inputs = fields.Datetime.from_string(odoo_datetime)
        vn_time = convert_utc_to_gmt_7(utc_datetime_inputs)
        vn_time_str = vn_time.strftime('%d/%m/%Y %H:%M')
        return vn_time_str
    else:
        return False
    
def convert_date_odoo_to_str_vn_date(odoo_date):
    if odoo_date:
        datetime_odoo = fields.Date.from_string(odoo_date)
        str_vn_date = datetime_odoo.strftime('%d/%m/%Y')
        return str_vn_date
    else:
        return False
    
def adict_flat(adict,item_seperate=';',k_v_separate = ':'):
    alist = []
    for k,v in adict.iteritems():
        if isinstance(v,dict):
            v = adict_flat(v,item_seperate=',',k_v_separate = ' ')
        alist.append(k + k_v_separate + v)
    return item_seperate.join(alist)     

def get_width(num_characters):
    return int((1+num_characters) * 256)
class DownloadCvi(http.Controller):
    @http.route('/web/binary/download_cvi',type='http', auth="public")
    def download_cvi(self,model,id, **kw):
        #print 'id',id
        #print '**kw**',kw
        #print  'model',model
        dlcv_obj = request.env[model].browse(int(id))
        #print 'dlcv_obj',dlcv_obj
        
        num2alpha = dict(zip(range(0, 26), string.ascii_uppercase))
        header_bold_style = xlwt.easyxf("font: bold on; pattern: pattern solid, fore_colour gray25;borders: left thin, right medium, top medium, bottom medium")
        normal_border_style = xlwt.easyxf("borders: left medium,right medium, top medium, bottom medium")
        cty_bold_style = xlwt.easyxf("font: bold on, height 256")# align: horiz centre, vert centre
        bold_style = xlwt.easyxf("font: bold on")
#         borders":{'left':'thin', 'right': 'thin', 'top': 'thin', 'bottom': 'thin
        if not request.env.user.user_has_groups('base.group_erp_manager'):
            company_ids = [request.env.user.company_id.id]
        else:
            company_ids = dlcv_obj.company_ids.ids or [request.env.user.company_id.id]
            
        
        records = request.env['cvi'].search([('company_id','in',company_ids),('loai_record','=',u'Công Việc')])
        user_ids = records.mapped('user_id')
        
        
        workbook = xlwt.Workbook()
        adict = [
            #('user_id',{'func': lambda val: val.name}),
                 ('ngay_bat_dau',{'func':convert_date_odoo_to_str_vn_date,'width':get_width(10)}),
                 ('code',{}),('tvcv_id_name',{'width':get_width(40)}),('noi_dung',{'width':get_width(40)}),
                 ('diem_tvi',{}),('so_luong',{}),('so_lan',{}),
                 ('diemtc',{'sum':True})
                # ,('diemld',{'sum':True})
                            ]
        offset_column = 1
        trungtam_row=0
        offset_thong_tin = 0
        sum_row = trungtam_row  +5
        title_row = trungtam_row + 7
        for user_id in user_ids:
            row_index = title_row + 1
            worksheet = workbook.add_sheet(user_id.name,cell_overwrite_ok=True)
            cvi_fields = request.env['cvi']._fields
            domain = [('user_id','=',user_id.id),('loai_record','=',u'Công Việc')]
            if dlcv_obj.ngay_bat_dau_filter:
                domain = expression.AND([[('ngay_bat_dau','>=',fields.Datetime.from_string(dlcv_obj.ngay_bat_dau_filter))],domain])
            if dlcv_obj.ngay_ket_thuc_filter:
                domain = expression.AND([[('ngay_bat_dau','<=',fields.Datetime.from_string(dlcv_obj.ngay_ket_thuc_filter))],domain])
                
                
            person_records = request.env['cvi'].search(domain,order='ngay_bat_dau')
            worksheet.write(trungtam_row, offset_column + 2,u'TRUNG TÂM HẠ TẦNG MẠNG MIỀN NAM',cty_bold_style)
            worksheet.write(trungtam_row + 1, offset_column + 2,u'ĐÀI VIỄN THÔNG HỒ CHÍ MINH',cty_bold_style)
            worksheet.write(trungtam_row + 3, offset_column + offset_thong_tin + 2,u'Họ và Tên')
            worksheet.write(trungtam_row + 3, offset_column  + offset_thong_tin + 3,user_id.name,bold_style)
            worksheet.write(trungtam_row + 4,offset_column  + offset_thong_tin + 2,u'Trạm')
            worksheet.write(trungtam_row  +4,offset_column   + offset_thong_tin + 3 ,user_id.company_id.name,bold_style)
            worksheet.write(sum_row, offset_column + offset_thong_tin + 2,u'Điểm Tổng')
            for title_column_index, field_from_my_adict in enumerate(adict):
                title_column_index += offset_column
                f_name,f_func_dict =  field_from_my_adict
                field = cvi_fields[f_name]
                f_string = field.string
                #print 'f_string',f_string
                worksheet.write(title_row, title_column_index,f_string,header_bold_style)
                width  = f_func_dict.get('width')
                if not width :
                    width = get_width(len(f_string))
                worksheet.col(title_column_index).width = width
#                 sum = f_func_dict.get('sum')
#                 if sum:
#                     worksheet.write(1, title_column_index,xlwt.Formula(sum))
                
            
            for r in person_records:#request.env['cvi'].search([]):
                for title_column_index, field_from_my_adict in enumerate(adict):
                    title_column_index += offset_column
                    f_name,f_func_dict =  field_from_my_adict
                    val = getattr(r, f_name)
                    func = f_func_dict.get('func',None)
                    if func:
                        val = func(val)
                    if val == False:
                        val = u''
#                     if val !=False:
                    worksheet.write(row_index, title_column_index,val,normal_border_style)
                row_index +=1
                

            for title_column_index, field_from_my_adict in enumerate(adict):
                title_column_index += offset_column
                f_name,f_func_dict =  field_from_my_adict
                field = cvi_fields[f_name]
                sum_a= f_func_dict.get('sum')
                if sum_a:
                    column_index_apha = num2alpha[title_column_index]
                    worksheet.write(sum_row, offset_column + offset_thong_tin + 3, xlwt.Formula('SUM(%s%s:%s%s)'%(column_index_apha,title_row + 2,column_index_apha,row_index)))
        
        response = request.make_response(None,
            headers=[('Content-Type', 'application/vnd.ms-excel'),
                    ('Content-Disposition', 'attachment; filename=table_cv_%s_%s.xls;'%(user_id.company_id.name,datetime.datetime.now().strftime('%d_%m_%H_%M')))],
           # cookies={'fileToken': token}
            )
        workbook.save(response.stream)

        return response
#         ALIGN_BORDER_dict = {'align':{'horiz': 'left','vert':'centre','wrap':'yes'},
#                      "borders":{'left':'thin', 'right': 'thin', 'top': 'thin', 'bottom': 'thin'}
#                      }
# 
#         title_format_dict = deepcopy(ALIGN_BORDER_dict)
#         title_format_dict['align']['horiz'] = 'centre'
#         title_format_dict['font'] = {"bold":"on"}
#         title_format_txt = adict_flat(title_format_dict)
#         title_format_style = xlwt.easyxf(title_format_txt)
#         normal_txt = adict_flat(ALIGN_BORDER_dict)
#         normal_style = xlwt.easyxf(normal_txt)
#         date_style = xlwt.easyxf(normal_txt, num_format_str='DD/MM/YYYY')
#         worksheet.write_merge(0, 0, 0 , 4,u"Danh sách Update thông tin đối tượng",title_format_style)
#         worksheet.write(1, 0,u"STT",title_format_style)
#     
#         worksheet.write(1, 1,u"Mã đối tượng",title_format_style)
#         worksheet.write(1, 2,u"Thuộc Tính",title_format_style)
#         worksheet.write(1, 3,u"Giá trị cập nhật",title_format_style)
#         worksheet.write(1, 4,u"Ghi chú",title_format_style)
#         row_index = 1
#         
#         
#         worksheet.col(1).width =int(20*260)
#         worksheet.col(2).width =int(25*260)
#         worksheet.col(3).width =int(20*260)
#             
#             
#         if mode_1900:
#             if sitetype=='3G':
#                 env = 'nodeb'
#             elif sitetype =='4G':
#                 env = 'enodeb'
#             elif sitetype=='2G':
#                 env='bts'
#             
#             for i in request.env[env].search([('ngay_bao_duong','=',False)]):
#                 row_index+=1
#                 worksheet.write(row_index, 1,i.ma_tram,normal_style)
#                 worksheet.write(row_index, 2, u'Thời gian bảo dưỡng',normal_style)
#                 worksheet.write(row_index, 3,datetime.date(1900, 1, 1),date_style)
#                 worksheet.write(row_index, 4, u'',normal_style)
# 
#                 row_index+=1
#                 worksheet.write(row_index, 1,i.ma_tram,normal_style)
#                 worksheet.write(row_index, 2, u'Đơn vị thực hiện',normal_style)
#                 worksheet.write(row_index, 3,u'Đài VT TGG',normal_style)
#                 worksheet.write(row_index, 4, u'',normal_style)
#         else:
#             import_tuan_id = id
#             model_class = request.env['importbdtuan']
#             import_tuan = model_class.browse(int(import_tuan_id))
#             lineimports = import_tuan.lineimports
#             loop = lineimports
#             for line in loop:
#                 if import_tuan.tuan_export and line.week_number !=import_tuan.tuan_export:
#                         continue
#                 if sitetype =='2G':
#                     ma_doi_tuong = line.bts_id.ma_tram
#                 elif sitetype=='3G':
#                     ma_doi_tuong = line.nodeb_id.ma_tram
#                 date_bd  = fields.Datetime.from_string(line.date)
#                 if ma_doi_tuong:
#                     row_index+=1
#                     worksheet.write(row_index, 1,ma_doi_tuong,normal_style)
#                     worksheet.write(row_index, 2, u'Thời gian bảo dưỡng',normal_style)
#                     worksheet.write(row_index, 3,date_bd,date_style)
#                     worksheet.write(row_index, 4, u'',normal_style)
#         fp = StringIO()
#         workbook.save(fp)
#         fp.seek(0)
#         data = fp.read()
#         fp.close()
        
#         return request.make_response(
#             data,
#             #self.from_data(columns_headers, rows),
#             headers=[
#                 ('Content-Disposition', 'attachment; filename="import_rnas_%s.xls"'%sitetype),
#                 ('Content-Type', 'application/octet-stream')
#             ],
#             #cookies={'fileToken': token}
#         )
        
        
    
class PivotInherit(pivot.TableExporter):
    @http.route('/web/pivot/export_xls_ahiihi', type='http', auth="user")
    def export_xls(self, data, token):
        jdata = json.loads(data)
        #print 'jdata_data',jdata
        nbr_measures = jdata['nbr_measures']
        #print '**nbr_measures**',nbr_measures
        
        workbook = xlwt.Workbook()
        worksheet = workbook.add_sheet(jdata['title'])
        header_bold = xlwt.easyxf("font: bold on; pattern: pattern solid, fore_colour gray25;")
        header_plain = xlwt.easyxf("pattern: pattern solid, fore_colour gray25;")
        bold = xlwt.easyxf("font: bold on;")

        # Step 1: writing headers
        headers = jdata['headers']
        #print 'headers',headers
        # x,y: current coordinates
        # carry: queue containing cell information when a cell has a >= 2 height
        #      and the drawing code needs to add empty cells below
        x, y, carry = 1, 0, deque()
        for i, header_row in enumerate(headers):
            #print 'i',i
            #print 'header_row',header_row
            worksheet.write(i, 0, '', header_plain)
            for header in header_row:
                #print 'for header in header_row, header', header
                while (carry and carry[0]['x'] == x):
                    #print 'carry',carry
                    cell = carry.popleft()
                    for i in range(nbr_measures):
                        worksheet.write(y, x+i, '', header_plain)
                    if cell['height'] > 1:
                        carry.append({'x': x, 'height': cell['height'] - 1})
                    x = x + nbr_measures
                style = header_plain if 'expanded' in header else header_bold
                for i in range(header['width']):
                    worksheet.write(y, x + i, header['title'] if i == 0 else '', style)
                if header['height'] > 1:
                    carry.append({'x': x, 'height': header['height'] - 1})
                x = x + header['width']
            while (carry and carry[0]['x'] == x):
                cell = carry.popleft()
                for i in range(nbr_measures):
                    worksheet.write(y, x+i, '', header_plain)
                if cell['height'] > 1:
                    carry.append({'x': x, 'height': cell['height'] - 1})
                x = x + nbr_measures
            x, y = 1, y + 1

        # Step 2: measure row
        if nbr_measures > 1:
            worksheet.write(y, 0, '', header_plain)
            for measure in jdata['measure_row']:
                style = header_bold if measure['is_bold'] else header_plain
                worksheet.write(y, x, measure['measure'], style)
                x = x + 1
            y = y + 1

        # Step 3: writing data
        x = 0
        for row in jdata['rows']:
            #print 'row',row
            worksheet.write(y, x, row['indent'] * '     ' + ustr(row['title']), header_plain)
            for cell in row['values']:
                x = x + 1
                if cell.get('is_bold', False):
                    worksheet.write(y, x, cell['value'], bold)
                else:
                    worksheet.write(y, x, cell['value'])
            x, y = 0, y + 1

        response = request.make_response(None,
            headers=[('Content-Type', 'application/vnd.ms-excel'),
                    ('Content-Disposition', 'attachment; filename=table.xls;')],
            cookies={'fileToken': token})
        workbook.save(response.stream)

        return response
        
        
class Binary(http.Controller):
    
    @api.multi
    @http.route('/web/binary/download_tuantra',type='http', auth="public")
    @serialize_exception
    def download_tuantra(self,id, **kw):
        
        
        workbook = xlwt.Workbook()
        worksheet = workbook.add_sheet('Sheet 1',cell_overwrite_ok=True)
        
        ALIGN_BORDER_dict = {'align':{'horiz': 'left','vert':'centre','wrap':'yes'},
                     "borders":{'left':'thin', 'right': 'thin', 'top': 'thin', 'bottom': 'thin'}
                     }

        title_format_dict = deepcopy(ALIGN_BORDER_dict)
        title_format_dict['align']['horiz'] = 'centre'
        title_format_dict['font'] = {"bold":"on"}
        title_format_txt = adict_flat(title_format_dict)
        title_format_style = xlwt.easyxf(title_format_txt)
        normal_txt = adict_flat(ALIGN_BORDER_dict)
        normal_style = xlwt.easyxf(normal_txt)
        
        
        worksheet.write_merge(0, 0, 0 , 15,u"BÁO CÁO TUẦN TRA NGÀY 20/09/2017",title_format_style)
        worksheet.write_merge(1, 2, 0 ,0,u"STT",title_format_style)
        worksheet.write_merge(1, 2, 1 ,1,u"Trạm",title_format_style)
        worksheet.write_merge(1, 2, 2 ,2,u"Hướng Tuyến",title_format_style)
        worksheet.write_merge(1, 2, 3 ,3,u"TTV – GSV",title_format_style)
        worksheet.write_merge(1, 2, 4 ,4,u"GPS",title_format_style)        
        worksheet.write_merge(1, 1, 5 ,6,u"LƯỢT ĐI",title_format_style)  
        worksheet.write_merge(2, 2, 5 ,5,u"GIỜ ĐI",title_format_style)  
        worksheet.write_merge(2, 2, 6 ,6,u"GIỜ ĐẾN",title_format_style)  

        worksheet.write_merge(1, 1, 7 ,8,u"LƯỢT VỀ",title_format_style)  
        worksheet.write_merge(2, 2, 7 ,7,u"GIỜ ĐI",title_format_style)  
        worksheet.write_merge(2, 2, 8 ,8,u"GIỜ ĐẾN",title_format_style) 
        
        worksheet.write_merge(1, 1, 9 ,10,u"SỐ ĐIỆN THOẠI",title_format_style)  
        worksheet.write_merge(2, 2, 9 ,9,u"ĐẦU TUYẾN",title_format_style)  
        worksheet.write_merge(2, 2, 10 ,10,u"CUỐI TUYẾN",title_format_style)  
         
        worksheet.write_merge(1, 2, 11 ,11,u"nội dung",title_format_style)

        worksheet.write_merge(1, 1, 12 ,14,u"KẾ HOẠCH NGÀY HÔM SAU",title_format_style)  
        worksheet.write_merge(2, 2, 12 ,12,u"Tuần tra",title_format_style)  
        worksheet.write_merge(2, 2, 13 ,13,u"Giám sát",title_format_style)  
        worksheet.write_merge(2, 2, 14,14,u"Bảo dưỡng – Xử Lý",title_format_style)  
        
        worksheet.write_merge(1, 2, 15 ,15,u"ghi chú",title_format_style)
        worksheet.write_merge(1, 2, 16 ,16,u"kiến nghị",title_format_style)
        
        
        fp = StringIO()
        workbook.save(fp)
        fp.seek(0)
        data = fp.read()
        fp.close()
        
        return request.make_response(
            data,
            #self.from_data(columns_headers, rows),
            headers=[
                ('Content-Disposition', 'attachment; filename="bao_cao_tuan_tra_cq.xls"'),
                ('Content-Type', 'application/octet-stream')
            ],
            #cookies={'fileToken': token}
        )
   
    
        
        
        
    @api.multi
    @http.route('/web/binary/download_document',type='http', auth="public")
    @serialize_exception
    def download_document(self,id, **kw):
        
        sitetype = kw['sitetype']
        if 'mode_1900' in kw:
            mode_1900 = True
        else:
            mode_1900 = False
            
        workbook = xlwt.Workbook()
        worksheet = workbook.add_sheet('Sheet 1',cell_overwrite_ok=True)
        
        ALIGN_BORDER_dict = {'align':{'horiz': 'left','vert':'centre','wrap':'yes'},
                     "borders":{'left':'thin', 'right': 'thin', 'top': 'thin', 'bottom': 'thin'}
                     }

        title_format_dict = deepcopy(ALIGN_BORDER_dict)
        title_format_dict['align']['horiz'] = 'centre'
        title_format_dict['font'] = {"bold":"on"}
        title_format_txt = adict_flat(title_format_dict)
        title_format_style = xlwt.easyxf(title_format_txt)
        normal_txt = adict_flat(ALIGN_BORDER_dict)
        normal_style = xlwt.easyxf(normal_txt)
        date_style = xlwt.easyxf(normal_txt, num_format_str='DD/MM/YYYY')
        worksheet.write_merge(0, 0, 0 , 4,u"Danh sách Update thông tin đối tượng",title_format_style)
        worksheet.write(1, 0,u"STT",title_format_style)
    
        worksheet.write(1, 1,u"Mã đối tượng",title_format_style)
        worksheet.write(1, 2,u"Thuộc Tính",title_format_style)
        worksheet.write(1, 3,u"Giá trị cập nhật",title_format_style)
        worksheet.write(1, 4,u"Ghi chú",title_format_style)
        row_index = 1
        
        
        worksheet.col(1).width =int(20*260)
        worksheet.col(2).width =int(25*260)
        worksheet.col(3).width =int(20*260)
            
            
        if mode_1900:
            if sitetype=='3G':
                env = 'nodeb'
            elif sitetype =='4G':
                env = 'enodeb'
            elif sitetype=='2G':
                env='bts'
            
            for i in request.env[env].search([('ngay_bao_duong','=',False)]):
                row_index+=1
                worksheet.write(row_index, 1,i.ma_tram,normal_style)
                worksheet.write(row_index, 2, u'Thời gian bảo dưỡng',normal_style)
                worksheet.write(row_index, 3,datetime.date(1900, 1, 1),date_style)
                worksheet.write(row_index, 4, u'',normal_style)

                row_index+=1
                worksheet.write(row_index, 1,i.ma_tram,normal_style)
                worksheet.write(row_index, 2, u'Đơn vị thực hiện',normal_style)
                worksheet.write(row_index, 3,u'Đài VT TGG',normal_style)
                worksheet.write(row_index, 4, u'',normal_style)
        else:
            import_tuan_id = id
            model_class = request.env['importbdtuan']
            import_tuan = model_class.browse(int(import_tuan_id))
            lineimports = import_tuan.lineimports
            loop = lineimports
            for line in loop:
                if import_tuan.tuan_export and line.week_number !=import_tuan.tuan_export:
                        continue
                if sitetype =='2G':
                    ma_doi_tuong = line.bts_id.ma_tram
                elif sitetype=='3G':
                    ma_doi_tuong = line.nodeb_id.ma_tram
                date_bd  = fields.Datetime.from_string(line.date)
                if ma_doi_tuong:
                    row_index+=1
                    worksheet.write(row_index, 1,ma_doi_tuong,normal_style)
                    worksheet.write(row_index, 2, u'Thời gian bảo dưỡng',normal_style)
                    worksheet.write(row_index, 3,date_bd,date_style)
                    worksheet.write(row_index, 4, u'',normal_style)
        fp = StringIO()
        workbook.save(fp)
        fp.seek(0)
        data = fp.read()
        fp.close()
        
        return request.make_response(
            data,
            #self.from_data(columns_headers, rows),
            headers=[
                ('Content-Disposition', 'attachment; filename="import_rnas_%s.xls"'%sitetype),
                ('Content-Type', 'application/octet-stream')
            ],
            #cookies={'fileToken': token}
        )


        

# -*- coding: utf-8 -*-
from odoo import models, fields, api,exceptions,tools,_
from odoo.osv import expression
from odoo.osv.query import Query



class DLCV(models.Model):
    _name = 'dlcv'
    ngay_bat_dau_filter = fields.Date()
    ngay_ket_thuc_filter = fields.Date()
    company_ids = fields.Many2many('res.company')
    member_ids = fields.Many2many('res.users')
    rs_cvi_ids = fields.Many2many('cvi')
    log =  fields.Text()
    log2 =  fields.Text()
    @api.multi
    def download_cvi(self):
        return {
             'type' : 'ir.actions.act_url',
             #'url': '/web/binary/download_document?model=importbd&field=file&id=%s&filename=product_stock.xls'%(self.id),
             'url': '/web/binary/download_cvi?model=dlcv&id=%s&more=abc'%(self.id),
             'target': 'self',
        }
           
    def cvi_filter(self):
        log = u''
        fields = self.env['cvi']._fields
        for k,v in fields.iteritems():
            break
        v.string
        log += u'string: %s\n type %s'%(v.string,v.type)
        self.log = log
        return True
        
#         args = [('loai_record','=',u'Công Việc')]
#         self._cr.execute(_sql)
#         kq_fetch =  self._cr.fetchall()
#         if self.ngay_bat_dau_filter:
#             '''SELECT "cvi".id FROM "cvi" WHERE (("cvi"."ngay_bat_dau" >= '2018-01-08 00:00:00')  AND  ("cvi"."loai_record" = 'Công Việc')) ORDER BY "cvi"."id" DESC '''
#             domain = [('loai_record','=',u'Công Việc')]
#             domain = expression.AND([[('ngay_bat_dau','>=',fields.Datetime.from_string(self.ngay_bat_dau_filter))],domain])
        args = [('company_id.name','ilike',u'ltk'),('loai_record','=',u'Công Việc')]
        domain = args
#         rs = self.env['cvi'].search(args)
#         self.rs_cvi_ids = rs
#         log = u''
#         _sql = ''' select sum(diemtc) from cvi '''
#         self._cr.execute(_sql)
#         kq_fetch =  self._cr.dictfetchall()
#         log +=u'%s'%kq_fetch
#         self.log = log
#         log = u''
#         if domain:
#             e = expression.expression(domain, self.env['cvi'])
#             log +='%s\n'%e
#             tables = e.get_tables()
#             log +='tables : %s\n'%tables
#             where_clause, where_params = e.to_sql()
#             log +='where_clause %s, where_params %s\n'%(where_clause, where_params)
#             where_clause = [where_clause] if where_clause else []
#         else:
#             where_clause, where_params, tables = [], [], ['"%s"' % self._table]
#         query =  Query(tables, where_clause, where_params)
#         log +='query : %s\n'%query
#         
#         order_by = self._generate_order_by(None, query)
#         log +='order_by : %s\n'%order_by
#         from_clause, where_clause, where_clause_params = query.get_sql()
#         log +='from_clause: %s, where_clause: %s, where_clause_params: %s\n'%(from_clause, where_clause, where_clause_params)
#         self.log = log
        log2 = u''
        log=u''
        log3=u''
        if domain:
            e = expression.expression(domain, self.env['cvi'])
            leafs= map(lambda leaf: leaf.leaf,e.result)
            log3 += '%s\n'%leafs
            log +='%s\n'%e
            tables = e.get_tables()
            log +='tables : %s\n'%tables
            where_clause, where_params = e.to_sql()
            log +='where_clause %s, where_params %s\n'%(where_clause, where_params)
            where_clause = [where_clause] if where_clause else []
        else:
            where_clause, where_params, tables = [], [], ['"%s"' % self._table]
        query =  Query(tables, where_clause, where_params)
        log +='query:%s\n'%query
        query = self.env['cvi']._where_calc(args)
        log2 +='query:%s\n'%query
#         self._apply_ir_rules(query, 'read')
#         order_by = self._generate_order_by(order, query)

        
        from_clause, where_clause, where_clause_params = query.get_sql()
        log2 +='from_clause: %s, where_clause: %s, where_clause_params: %s\n' %(from_clause, where_clause, where_clause_params)
        where_str = where_clause and (" WHERE %s" % where_clause) or ''
        query_str = 'SELECT %s.id FROM '%from_clause + from_clause + where_str
        self._cr.execute(query_str, where_clause_params)
        rs = self._cr.fetchall()
#         res = self._cr.dictfetchall()
        self.log = log
        self.log2 = log3
        
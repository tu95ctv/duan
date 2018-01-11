# -*- coding: utf-8 -*-
from odoo import models, fields, api,exceptions,tools,_
from odoo.addons.dai_tgg.mytools import  convert_odoo_datetime_to_vn_str,name_compute

class Comment(models.Model):
    _name = 'comment'
    name = fields.Char(compute='name_',store=True)
    noi_dung = fields.Text(string=u'Nội dung comment')
    cvi_id = fields.Many2one('cvi')
    file_ids = fields.Many2many('dai_tgg.file','comment_file_relate','comment_id','file_id',string=u'Files đính kèm')
    doitac_ids = fields.Many2many('res.partner',string=u'Đối Tác')
    giao_ca_id = fields.Many2one('ctr',string=u'Ca Trực')
    company_id = fields.Many2one('res.company',string=u'Công Ty')
    @api.model
    def create(self, vals):
        if not vals.get('company_id'):
            vals['company_id'] = self.env.user.company_id.id
        rs = super(Comment, self).create(vals)
        return rs
    
    
    @api.depends('noi_dung','create_uid','create_date')
    def name_(self):
#         def noi_dung_trim(noi_dung):
#             if noi_dung:
#                 if len(noi_dung) > 10:
#                     name = noi_dung[:10] + u'...'
#                     return name
#                 else:
#                     return noi_dung
        
        for r in self:
            name = name_compute(r, adict=[
                ('noi_dung',{'skip_if_False':True}),
                ('create_uid',{'pr':u'Người comment','skip_if_False':True,'func': lambda u:u.name}),
                ('create_date',{'func':convert_odoo_datetime_to_vn_str,'skip_if_False':True}),
                ] )
            r.name = name
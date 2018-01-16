# -*- coding: utf-8 -*-
import re
import base64
from odoo import models, fields, api,sql_db
import urllib2

class bds(models.Model):
    _name = 'bds.bds'
    name = fields.Char(compute = 'name_',store = True)
    title = fields.Char()
    images_ids = fields.One2many('bds.images','bds_id')
    siteleech_id = fields.Many2one('bds.siteleech')
    thumb = fields.Char()
    thumb_view = fields.Binary(compute='thumb_view_')   
    present_image_link = fields.Char()
    present_image_link_show = fields.Binary(compute='present_image_link_show_')
    
    poster_id = fields.Many2one('bds.poster')
    post_ids_of_user  = fields.One2many('bds.bds','poster_id',related='poster_id.post_ids')
    html = fields.Html()
    gia = fields.Float()
    area = fields.Float(digits=(32,1))
    address=fields.Char()
    quan_id = fields.Many2one('bds.quan',ondelete='restrict')
    phuong_id = fields.Many2one('bds.phuong')
    link = fields.Char()
    cho_tot_link_fake = fields.Char(compute='cho_tot_link_fake_')
    ngay_dang = fields.Datetime()
    
    count_chotot_post_of_poster = fields.Integer(related= 'poster_id.count_chotot_post_of_poster',store=True,string=u'chotot post quantity')
    count_bds_post_of_poster = fields.Integer(related= 'poster_id.count_bds_post_of_poster',store=True,string=u'bds post quantity')
    count_post_all_site = fields.Integer(related= 'poster_id.count_post_all_site',store=True)
    data = fields.Text()
    url_ids = fields.Many2many('bds.url','url_post_relate','post_id','url_id')
    @api.multi
    def cho_tot_link_fake_(self):
        for r in self:
            if 'chotot' in r.link:
                rs = re.search('/(\d*)$',r.link)
                id_link = rs.group(1)
                r.cho_tot_link_fake = 'https://nha.chotot.com/quan-10/mua-ban-nha-dat/' + 'xxx-' + id_link+ '.htm'
    @api.depends('thumb')
    def thumb_view_(self):
        for r in self:
            if r.thumb:
                photo = base64.encodestring(urllib2.urlopen(r.thumb).read())
                r.thumb_view = photo 
    @api.depends('present_image_link')
    def present_image_link_show_(self):
        for r in self:
            if r.present_image_link:
                photo = base64.encodestring(urllib2.urlopen(r.present_image_link).read())
                r.present_image_link_show = photo 

    @api.depends('title')
    def name_(self):
        self.name = self.title
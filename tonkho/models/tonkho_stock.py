# -*- coding: utf-8 -*-
from odoo import models, fields, api
from odoo.exceptions import UserError
from odoo.tools.translate import _
from odoo.tools.float_utils import float_compare

class PackOperation(models.Model):
    _inherit = "stock.pack.operation"
    ghi_chu = fields.Text(string=u'Ghi Chú')

    def get_qty_done_for_report(self):
        qty_done = self.qty_done
        int_qty_done = int(qty_done)
        if qty_done ==int_qty_done:
            return int_qty_done
        else:
            return qty_done
    @api.multi
    def _check_serial_number(self):
        for operation in self:
            if operation.picking_id and \
                    (operation.picking_id.picking_type_id.use_existing_lots or operation.picking_id.picking_type_id.use_create_lots) and \
                    operation.product_id and operation.product_id.tracking != 'none' and \
                    operation.qty_done > 0.0:
                if not operation.pack_lot_ids:
                    raise UserError(_('You need to provide a Lot/Serial Number for product in operation pack *1 %s') % operation.product_id.name)
                if operation.product_id.tracking == 'serial':
                    for opslot in operation.pack_lot_ids:
                        if opslot.qty not in (1.0, 0.0):
                            raise UserError(_('You should provide a different serial number for each piece'))        
    check_tracking = _check_serial_number
    @api.multi
    def action_split_lots(self):
        action_ctx = dict(self.env.context)
        # If it's a returned stock move, we do not want to create a lot
        returned_move = self.linked_move_operation_ids.mapped('move_id').mapped('origin_returned_move_id')
        picking_type = self.picking_id.picking_type_id
        state_not_in_done_cancel = self.state not in ['done','cancel']
        action_ctx.update({
            'serial': self.product_id.tracking == 'serial',
            'only_create': picking_type.use_create_lots and not picking_type.use_existing_lots and not returned_move,
            'state_not_in_done_cancel':state_not_in_done_cancel,
            'create_lots': picking_type.use_create_lots,
            'state_done': self.picking_id.state == 'done',
            'show_reserved': any([lot for lot in self.pack_lot_ids if lot.qty_todo > 0.0])})
        view_id = self.env.ref('stock.view_pack_operation_lot_form').id
        return {
            'name': _('Lot/Serial Number Details'),
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'stock.pack.operation',
            'views': [(view_id, 'form')],
            'view_id': view_id,
            'target': 'new',
            'res_id': self.ids[0],
            'context': action_ctx}
    split_lot = action_split_lots
        
class PackOperationLot(models.Model):
    _inherit = "stock.pack.operation.lot"
    ghi_chu = fields.Text(related='lot_id.ghi_chu')
    ghi_chu_for_create = fields.Text(string=u'Ghi chú Cho Tạo SN')
    pn = fields.Char(related='lot_id.pn', string=u'Part Number')
    pn_for_create = fields.Char(string=u'Part Number')
class StockProductionLot(models.Model):
    _inherit = "stock.production.lot"
    pn = fields.Char(string=u'Part Number')
    ghi_chu = fields.Text(string=u'Ghi chú')
class Quant(models.Model):
    """ Quants are the smallest unit of stock physical instances """
    _inherit = "stock.quant"
    pn = fields.Char(related='lot_id.pn')

class PT(models.Model):
    """ Quants are the smallest unit of stock physical instances """
    _inherit = 'product.template'
    type = fields.Selection(selection_add=[],default = 'product')
    
    
class StockMove(models.Model):
    _inherit = "stock.move"
    @api.multi
    def check_tracking(self, pack_operation):
        """ Checks if serial number is assigned to stock move or not and raise an error if it had to. """
        # TDE FIXME: I cannot able to understand
        for move in self:
            if move.picking_id and \
                    (move.picking_id.picking_type_id.use_existing_lots or move.picking_id.picking_type_id.use_create_lots) and \
                    move.product_id.tracking != 'none' and \
                    not (move.restrict_lot_id or (pack_operation and (pack_operation.product_id and pack_operation.pack_lot_ids)) or (pack_operation and not pack_operation.product_id)):
                raise UserError(_('You need to provide a Lot/Serial Number for product  4%s') % move.product_id.name)
                        
    
    
class StockLocation(models.Model):
    _inherit = 'stock.location'
    department_id =  fields.Many2one('hr.department')
    partner_id =  fields.Many2one('res.partner')

# -*- coding: utf-8 -*-
from odoo import _, api, fields, models, fields
from odoo.exceptions import ValidationError


class MRPProduction(models.Model):
    _inherit = 'mrp.production'

    optimal = fields.Boolean(
        compute='_compute_optimal'
    )

    @api.depends('bom_id', 'move_raw_ids')
    def _compute_optimal(self):
        self.optimal = True
        for move_raw in self.move_raw_ids:
            if move_raw.product_id.to_optimize:
                # for lot in move_raw.
                bom_line_id = self.bom_id.bom_line_ids.filtered(lambda r: r.product_id == move_raw.product_id)
                self.optimal = self.product_qty == int(move_raw.quantity_done / bom_line_id.product_qty)

    def _generate_raw_move(self, bom_line, line_data):
        if bom_line.product_id.to_optimize:
            line_data['qty'] = 0
        return super(MRPProduction, self)._generate_raw_move(bom_line, line_data)

    @api.multi
    def optimize(self):
        for move_raw in self.move_raw_ids:
            if move_raw.product_id.to_optimize:
                bom_line_id = self.bom_id.bom_line_ids.filtered(lambda r: r.product_id == move_raw.product_id)
                move_raw.state = 'assigned'
                self.product_qty = int(move_raw.quantity_done / bom_line_id.product_qty)
        changer = self.env['change.production.qty'].create({
            'mo_id': self.id,
            'product_qty': self.product_qty,
        })
        changer.change_prod_qty()

    @api.multi
    def open_produce_product(self):
        if not self.optimal:
            raise ValidationError(_('The production is not optimal'))
        return super(MRPProduction, self).open_produce_product()

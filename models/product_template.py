# -*- coding: utf-8 -*-
from odoo import _, api, fields, models, fields


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    to_optimize = fields.Boolean(
    )

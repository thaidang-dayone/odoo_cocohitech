from odoo import models, fields


class SupplierProduct(models.Model):
    _name = 'supplier.product'
    _description = 'Supplier Products'
    _rec_name = 'product_id'

    partner_id = fields.Many2one('res.partner', string='Supplier', required=True)
    product_id = fields.Many2one('product.product', string='Product', required=True)
    currency_id = fields.Many2one('res.currency', domain="[('name', 'in', ['VND','USD'])]")
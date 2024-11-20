from odoo import models, fields

class ResPartner(models.Model):
    _inherit = 'res.partner'

    is_china_partner = fields.Boolean(string='Is China Partner?')
    is_supplier = fields.Boolean(string='Is a Supplier')
    supplier_product_ids = fields.One2many('supplier.product', 'partner_id', string='Supplier Products')
    
class SupplierProduct(models.Model):
    _name = 'supplier.product'
    _description = 'Supplier Products'

    partner_id = fields.Many2one('res.partner', string='Supplier', required=True)
    product_id = fields.Many2one('product.product', string='Product', required=True)
    price = fields.Float(string='Price', required=True)
    currency_id = fields.Many2one('res.currency', string='Currency', required=True,
        default=lambda self: self.env.company.currency_id)
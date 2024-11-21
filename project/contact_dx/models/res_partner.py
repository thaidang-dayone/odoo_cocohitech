from odoo import models, fields

class ResPartner(models.Model):
    _inherit = 'res.partner'

    is_china_partner = fields.Boolean(string='Is China Partner?')
    is_supplier = fields.Boolean(string='Is a Supplier')
    supplier_product_ids = fields.One2many('supplier.product', 'partner_id', string='Supplier Products')
    

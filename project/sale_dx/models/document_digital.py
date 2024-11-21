from odoo import models, fields, api

class DocumentDigital(models.Model):
    _name = 'document.digital'
    _description = 'Digital Document'

    name = fields.Char(string='Document Name', required=True)
    description = fields.Text(string='Description')
    active = fields.Boolean(string='Active', default=True)
    
class SaleOrderDocumentCost(models.Model):
    _name = 'sale.order.document.cost'
    _description = 'Sale Order Document Costs'

    sale_order_id = fields.Many2one('sale.order', string='Sale Order', required=True, ondelete='cascade')
    document_id = fields.Many2one('document.digital', string='Document', required=True)
    cost = fields.Monetary(string='Cost', required=True)
    currency_id = fields.Many2one('res.currency', related='sale_order_id.currency_id', store=True)
    upload_date = fields.Datetime(string='Upload Date', default=fields.Datetime.now)
    document_file = fields.Binary(string='Document File', required=True)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('done', 'Done'),
        ('cancel', 'Cancel'),
    ], string='Status', default='draft')
    
class SaleOrderSupplierProduct(models.Model):
    _name = 'sale.order.supplier.product'
    _description = 'Sale Order Supplier Product Costs'

    sale_order_id = fields.Many2one('sale.order', string='Sale Order', required=True, ondelete='cascade')
    supplier_product_id = fields.Many2one('supplier.product', string='Supplier Product', required=True)
    cost = fields.Monetary(string='Cost', compute='_compute_cost', store=True)
    quantity = fields.Float(string='Quantity', default=1)
    currency_id = fields.Many2one('res.currency', related='sale_order_id.currency_id', store=True)
    
    @api.depends('supplier_product_id', 'supplier_product_id.price')
    def _compute_cost(self):
        for record in self:
            record.cost = record.supplier_product_id.price * record.quantity
    
    
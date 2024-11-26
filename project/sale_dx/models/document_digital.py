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
    _rec_name = 'document_id'

    sale_order_id = fields.Many2one('sale.order', string='Sale Order', required=True, ondelete='cascade')
    document_id = fields.Many2one('document.digital', string='Document', required=True)
    cost = fields.Monetary(string='Cost', required=True)
    currency_id = fields.Many2one('res.currency', domain="[('name', 'in', ['VND','USD','CNY'])]")
    upload_date = fields.Datetime(string='Upload Date', default=fields.Datetime.now)
    document_file = fields.Binary(string='Document File')
    state = fields.Selection([
        ('draft', 'Draft'),
        ('done', 'Done'),
        ('cancel', 'Cancel'),
    ], string='Status', default='draft')
    
    def action_done(self):
        self.state = 'done'
    
    def action_cancel(self):
        self.state = 'cancel'
        
    
class SaleOrderSupplierProduct(models.Model):
    _name = 'sale.order.supplier.product'
    _description = 'Sale Order Supplier Product Costs'
    _rec_name = 'supplier_product_id'
    

    sale_order_id = fields.Many2one('sale.order', string='Sale Order', required=True, ondelete='cascade')
    supplier_id = fields.Many2one('res.partner', related='sale_order_id.supplier_id', store=True)
    supplier_product_id = fields.Many2one('supplier.product', string='Supplier Product', required=True,
        domain ="[('partner_id', '=', supplier_id)]")
    cost = fields.Monetary(string='Cost', compute='_compute_cost', store=True)
    quantity = fields.Float(string='Quantity', default=1)
    price = fields.Float(string='Price')
    currency_id = fields.Many2one('res.currency', domain="[('name', 'in', ['VND','USD'])]")
    
    @api.depends('supplier_product_id', 'quantity', 'price')
    def _compute_cost(self):
        for record in self:
            record.cost = record.supplier_product_id.price * record.quantity
           
class OtherCosts(models.Model):
    _name = 'sale.order.other.costs'
    _description = 'Other Costs'
    

    name = fields.Char(string='Cost Name', required=True)
    cost_type = fields.Selection([
        ('shipping', 'Shipping'),
        ('quarantine', 'Quarantine'),
        ('commission', 'Commission'),
        ('other', 'Other'),
    ], string='Cost Type', required=True)
    cost = fields.Monetary(string='Cost', required=True)
    currency_id = fields.Many2one('res.currency', domain="[('name', 'in', ['VND','USD','CNY'])]")
    sale_order_id = fields.Many2one('sale.order', string='Sale Order', ondelete='cascade')
    
    
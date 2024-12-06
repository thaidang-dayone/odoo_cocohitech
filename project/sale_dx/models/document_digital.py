from odoo import models, fields, api


class DocumentDigital(models.Model):
    _name = 'document.digital'
    _description = 'Digital Document'

    name = fields.Char(string='Document Name', required=True)
    currency_id = fields.Many2one('res.currency', domain="[('name', 'in', ['VND','USD','CNY'])]")
    description = fields.Text(string='Description')
    active = fields.Boolean(string='Active', default=True)


class SaleOrderDocumentCost(models.Model):
    _name = 'sale.order.document.cost'
    _description = 'Sale Order Document Costs'
    _rec_name = 'document_id'

    sale_order_id = fields.Many2one('sale.order', string='Sale Order', required=True, ondelete='cascade')
    document_id = fields.Many2one('document.digital', string='Document', required=True)
    cost = fields.Monetary(string='Cost', required=True)
    currency_id = fields.Many2one('res.currency', related='document_id.currency_id', store=True)
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
                                          domain="[('partner_id', '=', supplier_id)]")
    product_id = fields.Many2one('product.product', related='supplier_product_id.product_id', store=True,
                                 string='Product')
    cost = fields.Monetary(string='Cost', compute='_compute_cost', store=True)
    quantity = fields.Float(string='Quantity', default=1)
    price = fields.Float(string='Price')
    currency_id = fields.Many2one('res.currency', related='supplier_product_id.currency_id')
    uom_id = fields.Many2one('uom.uom', string='OuM', compute='_compute_uom')

    @api.depends('product_id')
    def _compute_uom(self):
        for record in self:
            if record.product_id:

                product_template = record.product_id.product_tmpl_id
                record.uom_id = product_template.uom_id if product_template else False
            else:
                record.uom_id = False

    @api.depends('supplier_product_id', 'quantity', 'price')
    def _compute_cost(self):
        for record in self:
            record.cost = record.price * record.quantity


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
    description = fields.Text(string='Description')
    sale_order_id = fields.Many2one('sale.order', string='Sale Order', ondelete='cascade')
    quantity = fields.Float(string='Quantity', default=1.0, required=True)
    unit_price = fields.Monetary(string='Unit Price', required=True)
    cost_vnd = fields.Monetary(string='Cost VND', compute='_compute_cost_vnd', store=True,
                               currency_field='currency_id_vnd')
    currency_id_vnd = fields.Many2one('res.currency', string='Currency VND',
                                      default=lambda self: self.env.ref('base.VND').id)

    @api.onchange('quantity', 'unit_price')
    def _onchange_cost(self):
        """Automatically update the cost based on quantity and unit price."""
        for record in self:
            record.cost = record.quantity * record.unit_price

    @api.depends('cost', 'currency_id')
    def _compute_cost_vnd(self):
        """Automatically update the cost in VND based on the currency."""
        for record in self:
            if record.currency_id:

                sale_order = self.env['sale.order'].browse(record.sale_order_id.id)
                if record.currency_id.name == 'VND':
                    record.cost_vnd = record.cost
                elif record.currency_id.name == 'USD':
                    usd_vnd_rate = sale_order.usd_vnd_rate_1
                    record.cost_vnd = record.cost * usd_vnd_rate if usd_vnd_rate else 0.0
                elif record.currency_id.name == 'CNY':
                    rmb_vnd_rate = sale_order.rmb_vnd_rate_1
                    record.cost_vnd = record.cost * rmb_vnd_rate if rmb_vnd_rate else 0.0
                else:
                    record.cost_vnd = 0.0  # Giá trị mặc định nếu không tìm thấy tỷ giá

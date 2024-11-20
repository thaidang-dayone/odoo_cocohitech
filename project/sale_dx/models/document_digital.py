from odoo import models, fields, api

class DocumentDigital(models.Model):
    _name = 'document.digital'
    _description = 'Digital Document'

    name = fields.Char(string='Document Name', required=True)
    type_id = fields.Many2one('document.digital.type', string='Document Type')
    document_file = fields.Binary(string='Document File', required=True)
    description = fields.Text(string='Description')
    upload_date = fields.Datetime(string='Upload Date', default=fields.Datetime.now)
    price = fields.Float(string='Price')
    state = fields.Selection([
        ('draft', 'Draft'),
        ('done', 'Done'),
        ('cancel', 'Cancel'),
    ], string='Status', default='draft')
    # owner_id = fields.Many2one('res.users', string='Owner', default=lambda self: self.env.user)
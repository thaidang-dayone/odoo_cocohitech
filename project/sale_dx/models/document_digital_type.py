from odoo import models, fields

class DocumentDigitalType(models.Model):
    _name = 'document.digital.type'
    _description = 'Document Digital Type'

    name = fields.Char(string='Name', required=True)
    description = fields.Text(string='Description')
    active = fields.Boolean(string='Active', default=True)
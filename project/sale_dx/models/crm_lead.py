from odoo import models, fields

class CrmLead(models.Model):
    _inherit = 'crm.lead'

    estimated_departure_date = fields.Datetime(string='Estimated Departure Date')
    estimated_arrival_date = fields.Datetime(string='Estimated Arrival Date')
    
    def _prepare_sale_order_values(self, customer, team_id=False):
        values = super(CrmLead, self)._prepare_sale_order_values(customer, team_id)
        values.update({
            'estimated_departure_date': self.estimated_departure_date,
            'estimated_arrival_date': self.estimated_arrival_date,
        })
        return values
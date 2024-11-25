from odoo import models, fields, api
from datetime import datetime, timedelta


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    estimated_departure_date = fields.Datetime(string='Estimated Departure Date')
    estimated_arrival_date = fields.Datetime(string='Estimated Arrival Date')
    is_overdue = fields.Boolean(string='Is Overdue', compute='_compute_is_overdue', store=True)

    @api.depends('estimated_arrival_date', 'remaining_amount')
    def _compute_is_overdue(self):
        for order in self:
            if order.estimated_arrival_date:
                overdue_date = order.estimated_arrival_date + timedelta(days=5)
                if datetime.now() > overdue_date and order.remaining_amount > 0:
                    order.is_overdue = True
                else:
                    order.is_overdue = False
            else:
                order.is_overdue = False

    def _compute_color(self):
        for order in self:
            if order.is_overdue:
                order.color = 2  # Red color
            else:
                order.color = 0  # Default color

    color = fields.Integer(string='Color', compute='_compute_color', store=True)
from odoo import models, fields, api
from odoo.exceptions import ValidationError

from random import randint
from datetime import datetime, timedelta


class SaleOrder(models.Model):
    _inherit = 'sale.order'
    
    def _default_color(self):
        list_num = [0, 1, 3, 8]
        return list_num[randint(0, 3)]
    
    supplier_id = fields.Many2one('res.partner', string='Supplier')
    document_cost_ids = fields.One2many(
        'sale.order.document.cost', 
        'sale_order_id', 
        string='Document Costs'
    )
    supplier_product_cost_ids = fields.One2many(
        'sale.order.supplier.product', 
        'sale_order_id', 
        string='Supplier Product Costs'
    )
    other_cost_ids = fields.One2many(
        'sale.order.other.costs',
        'sale_order_id',
        string='Other Costs'
    )
    # Exchange Rates
    usd_vnd_rate = fields.Float(
        string='USD/VND Exchange Rate', 
        digits=(12, 2),
        default=lambda self: self._get_current_usd_vnd_rate()
    )
    # Deposit and Remaining Amount
    deposit_amount = fields.Monetary(
        string='Deposit Amount', 
        currency_field='currency_id'
    )
    remaining_amount = fields.Monetary(
        string='Remaining Amount', 
        currency_field='currency_id', 
        compute='_compute_remaining_amount', 
        store=True
    )
    # Chinese Customer Specific Fields
    is_china_partner = fields.Boolean(
        related='partner_id.is_china_partner', 
        string='Is Chinese Partner'
    )
    rmb_vnd_rate = fields.Float(
        string='RMB/VND Exchange Rate', 
        digits=(12, 2),
        default=lambda self: self._get_current_rmb_vnd_rate()
    )
    rmb_usd_rate = fields.Float(
        string='RMB/USD Exchange Rate', 
        digits=(12, 2),
        default=lambda self: self._get_current_rmb_usd_rate()
    )

    # Chinese Customer Special Processing
    china_partner_adjustment = fields.Monetary(
        string='China Partner Price Adjustment', 
        compute='_compute_china_partner_special_processing', store=True
    )
    china_partner_cash_conversion = fields.Monetary(
        string='Cash Conversion Amount', 
        store=True,
        compute='_compute_china_partner_special_processing',
    )
    #Compute amounts
    total_supplier_product_cost = fields.Monetary(
        string='Total Supplier Product Prices', 
        compute='_compute_total_costs',
        store=True
    )
    total_document_cost = fields.Monetary(
        string='Total Document Costs', 
        compute='_compute_total_costs',
        store=True
    )
    other_costs = fields.Monetary(
        string='Other Costs', 
        compute='_compute_total_costs',
        store=True
    )
    total_all_costs = fields.Monetary(
        string='Total costs', 
        compute='_compute_total_costs',
        store=True
    )
    total_revenue = fields.Monetary(
        string='Total Revenue', 
        compute='_compute_revenue_details',
        store=True
    )
    total_profit = fields.Monetary(
        string='Total Profit', 
        compute='_compute_revenue_details',
        store=True
    )
    profit_percentage = fields.Float(
        string='Profit Percentage(%)', 
        compute='_compute_revenue_details',
        store=True
    )
    # money with vnd
    total_amount_vnd = fields.Monetary(
        string='Total Amount VND', 
        compute='_compute_price_convert_totals',
        store=True
    )
    
    state_transfer = fields.Selection([
        ('draft_cont', 'Lấy rỗng'),
        ('ready_to_pick', 'Kéo cont tới kho'),
        ('packed', 'Đóng hàng đầy'),
        ('ready_to_ship', 'Kéo lên cảng chờ xuất'),
        ('reported', 'Tờ khai phân luồng'),
        ('ready_to_load', 'Sẵn sàng lên tàu'),
        ('exported', 'Xuất khẩu')
    ], string='State Transfer', default='draft_cont')
    
    color_report = fields.Integer(string='Color Reported', default=_default_color)
    
    estimated_departure_date = fields.Datetime(string='Estimated Departure Date')
    estimated_arrival_date = fields.Datetime(string='Estimated Arrival Date')
    is_overdue = fields.Boolean(string='Is Overdue', compute='_compute_is_overdue', store=True)
    is_received_rmb = fields.Boolean(string='Is Received', default=False)

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
    
    def action_to_ready_to_pick(self):
        self.state_transfer = 'ready_to_pick'
    
    def action_to_packed(self):
        self.state_transfer = 'packed'
    
    def action_to_ready_to_ship(self):
        self.state_transfer = 'ready_to_ship'
    
    def action_to_reported(self):
        self.state_transfer = 'reported'
    
    def action_to_ready_to_load(self):
        self.state_transfer = 'ready_to_load'
    
    def action_to_exported(self):
        self.state_transfer = 'exported'

    @api.depends_context('lang') 
    @api.depends('currency_id', 'amount_total', 'usd_vnd_rate' )
    def _compute_price_convert_totals(self):
        for order in self:
            order.total_amount_vnd = order.amount_total*order.usd_vnd_rate
    
    @api.model_create_multi
    def create(self, vals):
        order = super(SaleOrder, self).create(vals)
        if 'deposit_amount' in vals and vals['deposit_amount'] > 0:
            order._add_or_update_special_deduction_line()
        return order

    def write(self, vals):
        res = super(SaleOrder, self).write(vals)
        if 'deposit_amount' in vals and vals['deposit_amount'] > 0:
            self._add_or_update_special_deduction_line()
        return res

    def _add_or_update_special_deduction_line(self):
        for order in self:
            deduction_line = order.order_line.filtered(lambda line: line.name == 'Special Deduction')
            if deduction_line:
                deduction_line.price_unit = -order.deposit_amount
            else:
                self.env['sale.order.line'].create({
                    'order_id': order.id,
                    'name': 'Special Deduction',
                    'product_uom_qty': 1,
                    'price_unit': -order.deposit_amount,
                    'product_id': self.env.ref('sale_dx.product_product_consultant_deposit').id,
                })
    
    @api.depends('amount_total', 'deposit_amount')
    def _compute_remaining_amount(self):
        for order in self:
            order.remaining_amount = order.amount_total

    def _get_current_usd_vnd_rate(self):
        # Implement logic to fetch current USD/VND rate
        # Could be from an external API or manual input
        return 24000  # Example rate

    def _get_current_rmb_vnd_rate(self):
        # Implement logic to fetch current RMB/VND rate
        return 3500  # Example rate

    def _get_current_rmb_usd_rate(self):
        # Implement logic to fetch current RMB/USD rate
        return 0.14  # Example rate

    @api.depends('deposit_amount')
    def _compute_china_partner_special_processing(self):
        """
        Special processing for Chinese partners
        - Calculate cash conversion
        """
        for order in self:
            if order.is_china_partner:
            #     raise ValidationError("This method is only for Chinese partners")
            
            # Store the price adjustment
                order.china_partner_adjustment = order.deposit_amount
                order.china_partner_cash_conversion = order.deposit_amount/order.rmb_usd_rate
        
    
    def confirm_receive_deposit(self):
        for order in self:
            if order.is_china_partner:
                order.is_received_rmb = True
                order.china_partner_adjustment = 0
            order._compute_revenue_details()

    @api.depends(
        'supplier_product_cost_ids', 
        'document_cost_ids', 
        'other_cost_ids',
    )
    def _compute_total_costs(self):
        for order in self:
            total_supplier_product_cost = 0
            total_document_cost = 0
            total_other_costs = 0
            
            # Quy đổi giá của các sản phẩm về VND
            for supplier_product_cost in order.supplier_product_cost_ids:
                if supplier_product_cost.currency_id != self.env.ref('base.VND'):
                    rate = order.usd_vnd_rate if supplier_product_cost.currency_id == self.env.ref('base.USD') else 1
                    total_supplier_product_cost += supplier_product_cost.cost * rate
                else:
                    total_supplier_product_cost += supplier_product_cost.cost
            
            for document_cost in order.document_cost_ids:
                if document_cost.currency_id != self.env.ref('base.VND'):
                    rate = order.usd_vnd_rate if document_cost.currency_id == self.env.ref('base.USD') else order.rmb_vnd_rate
                    total_document_cost += document_cost.cost * rate
                else:
                    total_document_cost += document_cost.cost
            
            for other_cost in order.other_cost_ids:
                if other_cost.currency_id != self.env.ref('base.VND'):
                    rate = order.usd_vnd_rate if document_cost.currency_id == self.env.ref('base.USD') else order.rmb_vnd_rate
                    total_other_costs += other_cost.cost * rate
                else:
                    total_other_costs += other_cost.cost
            
            order.total_supplier_product_cost = total_supplier_product_cost
            order.total_document_cost = total_document_cost
            order.other_costs = total_other_costs
            order.total_all_costs = total_supplier_product_cost + total_document_cost + total_other_costs

    @api.depends(
        'amount_total', 
        'total_amount_vnd',
        'total_all_costs', 
        'china_partner_adjustment',
        'china_partner_cash_conversion',
        'is_received_rmb'
    )
    def _compute_revenue_details(self):
        for order in self:
            # Tổng doanh thu (trừ điều chỉnh cho khách Trung Quốc nếu có)
            order.total_revenue = order.total_amount_vnd - (
                order.china_partner_adjustment or 0
            )
            # Tổng lợi nhuận
            order.total_profit = order.total_revenue - order.total_all_costs
            if order.is_received_rmb:
                order.total_profit += order.china_partner_cash_conversion*order.rmb_vnd_rate

    def action_confirm(self):
        """
        Ghi đè phương thức xác nhận đơn hàng để bổ sung logic tính toán chi phí
        """
        # Thực hiện tính toán cuối cùng trước khi xác nhận
        self._compute_total_costs()
        self._compute_revenue_details()
        
        return super().action_confirm()
        
    
from odoo import models, fields, api
from odoo.exceptions import ValidationError

class SaleOrder(models.Model):
    _inherit = 'sale.order'

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
        digits=(12, 0),
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
        digits=(12, 0),
        default=lambda self: self._get_current_rmb_vnd_rate()
    )
    rmb_usd_rate = fields.Float(
        string='RMB/USD Exchange Rate', 
        digits=(12, 0),
        default=lambda self: self._get_current_rmb_usd_rate()
    )

    # Chinese Customer Special Processing
    china_partner_adjustment = fields.Monetary(
        string='China Partner Price Adjustment', 
        currency_field='currency_id'
    )
    china_partner_cash_conversion = fields.Monetary(
        string='Cash Conversion Amount', 
        currency_field='currency_id'
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
                    'product_id': self.env.ref('product.product_product_consultant_deposit').id,
                })
    
    @api.depends('amount_total', 'deposit_amount')
    def _compute_remaining_amount(self):
        for order in self:
            order.remaining_amount = order.amount_total - order.deposit_amount

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

    def process_china_partner_invoice(self, adjusted_amount):
        """
        Special processing for Chinese partners
        - Adjust invoice amount
        - Calculate cash conversion
        """
        self.ensure_one()
        if not self.is_china_partner:
            raise ValidationError("This method is only for Chinese partners")
        
        # Store the price adjustment
        self.china_partner_adjustment = self.amount_total - adjusted_amount
        
        # Calculate cash conversion based on RMB/USD rate
        cash_conversion_usd = self.china_partner_adjustment
        cash_conversion_rmb = cash_conversion_usd * self.rmb_usd_rate
        self.china_partner_cash_conversion = cash_conversion_rmb

        # Optionally create an account move for tracking
        self._create_china_partner_adjustment_move()

    def _create_china_partner_adjustment_move(self):
        """
        Create an account move to track the price adjustment
        """
        move_vals = {
            'move_type': 'entry',
            'ref': f'China Partner Adjustment - {self.name}',
            'sale_order_id': self.id,
            'journal_id': self.env['account.journal'].search([('type', '=', 'misc')], limit=1).id,
            'line_ids': [
                (0, 0, {
                    'name': 'Price Adjustment',
                    'debit': self.china_partner_adjustment,
                    'credit': 0,
                    'account_id': self.env['account.account'].search([('account_type', '=', 'expense')], limit=1).id,
                }),
                (0, 0, {
                    'name': 'Cash Conversion',
                    'debit': 0,
                    'credit': self.china_partner_cash_conversion,
                    'account_id': self.env['account.account'].search([('account_type', '=', 'liability_current')], limit=1).id,
                })
            ]
        }
        return self.env['account.move'].create(move_vals)
    

    @api.depends(
        'supplier_product_cost_ids.cost', 
        'document_cost_ids.cost', 
        'other_costs'
    )
    def _compute_total_costs(self):
        for order in self:
            order.total_supplier_product_cost = sum(
                order.supplier_product_cost_ids.mapped('cost')
            )
            
            order.total_document_cost = sum(
                order.document_cost_ids.mapped('cost')
            )
            order.other_costs = sum(
                order.other_cost_ids.mapped('cost')
            )
            order.total_all_costs = (
                order.total_supplier_product_cost + 
                order.total_document_cost + 
                order.other_costs
            )

    @api.depends(
        'amount_total', 
        'total_all_costs', 
        'china_partner_adjustment'
    )
    def _compute_revenue_details(self):
        for order in self:
            # Tổng doanh thu (trừ điều chỉnh cho khách Trung Quốc nếu có)
            order.total_revenue = order.amount_total - (
                order.china_partner_adjustment or 0
            )
            # Tổng lợi nhuận
            order.total_profit = order.total_revenue - order.total_all_costs
            # Tỷ lệ lợi nhuận
            order.profit_percentage = (
                (order.total_profit / order.total_revenue) * 100 
                if order.total_revenue > 0 else 0
            )

    def _get_adjustment_account(self):
        """
        Lấy tài khoản điều chỉnh
        """
        return self.env['account.account'].search([
            ('account_type', '=', 'expense')
        ], limit=1).id

    def _get_revenue_account(self):
        """
        Lấy tài khoản doanh thu
        """
        return self.env['account.account'].search([
            ('account_type', '=', 'income')
        ], limit=1).id

    def action_confirm(self):
        """
        Ghi đè phương thức xác nhận đơn hàng để bổ sung logic tính toán chi phí
        """
        # Thực hiện tính toán cuối cùng trước khi xác nhận
        self._compute_total_costs()
        self._compute_revenue_details()
        
        return super().action_confirm()
        
    
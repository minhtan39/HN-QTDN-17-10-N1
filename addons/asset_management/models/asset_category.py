from odoo import models, fields, api


class AssetCategory(models.Model):
    _name = 'asset.category'
    _description = 'Loại tài sản'

    name = fields.Char(
        string='Tên loại tài sản',
        required=True
    )

    code = fields.Char(
        string='Mã loại'
    )

    description = fields.Text(
        string='Mô tả'
    )

    management_type = fields.Selection(
        [
            ('quantity', 'Quản lý theo số lượng'),
            ('individual', 'Quản lý từng tài sản'),
        ],
        string='Cách quản lý',
        required=True,
        default='quantity'
    )

    total_quantity = fields.Integer(
        string='Tổng số lượng',
        default=0
    )

    used_quantity = fields.Integer(
        string='Đã sử dụng',
        compute='_compute_used_quantity'
    )

    available_quantity = fields.Integer(
        string='Còn lại',
        compute='_compute_available_quantity'
    )

    # =========================
    # COMPUTE USED QUANTITY
    # =========================
    @api.depends('total_quantity')
    def _compute_used_quantity(self):
        for record in self:
            used = self.env['asset.history'].search([
                ('category_id', '=', record.id),
                ('status', '=', 'using')
            ])
            record.used_quantity = sum(used.mapped('quantity'))

    # =========================
    # COMPUTE AVAILABLE
    # =========================
    @api.depends('total_quantity', 'used_quantity')
    def _compute_available_quantity(self):
        for record in self:
            record.available_quantity = record.total_quantity - record.used_quantity

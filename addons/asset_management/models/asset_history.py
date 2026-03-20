from odoo import models, fields, api
from odoo.exceptions import ValidationError


class AssetHistory(models.Model):
    _name = 'asset.history'
    _description = 'Lịch sử mượn tài sản'
    _order = 'start_date desc'

    # =========================
    # THÔNG TIN MƯỢN
    # =========================
    category_id = fields.Many2one(
        'asset.category',
        string='Loại tài sản',
        required=True
    )

    employee_id = fields.Many2one(
        'hr.employee',
        string='Nhân viên',
        required=True
    )

    location_id = fields.Many2one(
        'asset.location',
        string='Vị trí tài sản'
    )

    quantity = fields.Integer(
        string='Số lượng mượn',
        default=1,
        required=True
    )

    start_date = fields.Date(
        string='Ngày mượn',
        default=fields.Date.today,
        required=True
    )

    end_date = fields.Date(
        string='Ngày trả'
    )

    # =========================
    # TRẠNG THÁI
    # =========================
    status = fields.Selection(
        [
            ('using', 'Đang mượn'),
            ('returned', 'Đã trả'),
        ],
        string='Trạng thái',
        default='using',
        required=True
    )

    # =========================
    # THIỆT HẠI KHI TRẢ
    # =========================
    damage_type = fields.Selection(
        [
            ('none', 'Không thiệt hại'),
            ('broken', 'Hỏng'),
            ('lost', 'Mất'),
            ('other', 'Khác'),
        ],
        string='Loại thiệt hại',
        default='none'
    )

    damage_cost = fields.Float(
        string='Chi phí thiệt hại'
    )

    damage_note = fields.Text(
        string='Ghi chú thiệt hại'
    )

    # =========================
    # TỔNG THIỆT HẠI (THỐNG KÊ)
    # =========================
    total_damage_cost = fields.Float(
        string='Tổng chi phí thiệt hại',
        compute='_compute_total_damage_cost',
        store=True
    )

    @api.depends('damage_cost', 'status')
    def _compute_total_damage_cost(self):
        for record in self:
            record.total_damage_cost = (
                record.damage_cost if record.status == 'returned' else 0.0
            )

    # ===============================
    # VALIDATE SỐ LƯỢNG MƯỢN
    # ===============================
    @api.constrains('quantity', 'category_id', 'status')
    def _check_quantity(self):
        for record in self:
            if record.status != 'using':
                continue

            if not record.category_id:
                continue

            if record.category_id.management_type != 'quantity':
                continue

            if record.quantity <= 0:
                raise ValidationError("Số lượng mượn phải lớn hơn 0")

            if record.quantity > record.category_id.available_quantity:
                raise ValidationError(
                    f"Số lượng mượn vượt quá tồn kho "
                    f"({record.category_id.available_quantity})"
                )

    # =========================
    # TRẢ TÀI SẢN
    # =========================
    def action_return(self):
        default_location = self.env['asset.location'].search(
            [('is_default', '=', True)], limit=1
        )

        for record in self:
            if record.status == 'returned':
                raise ValidationError("Tài sản này đã được trả rồi.")

            if record.damage_type != 'none' and record.damage_cost <= 0:
                raise ValidationError("Vui lòng nhập chi phí thiệt hại.")

            record.write({
                'status': 'returned',
                'end_date': fields.Date.today(),
                'location_id': default_location.id if default_location else False
            })

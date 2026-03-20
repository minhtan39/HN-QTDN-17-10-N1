from odoo import models, fields, api
from datetime import date


class AssetAsset(models.Model):
    _name = 'asset.asset'
    _description = 'Tài sản công ty'

    name = fields.Char(
        string='Tên tài sản',
        required=True
    )


    category_id = fields.Many2one(
        'asset.category',
        string='Loại tài sản',
        required=True
    )



    assigned_employee_id = fields.Many2one(
        'hr.employee',
        string='Nhân viên đang sử dụng'
    )

    status = fields.Selection(
        [
            ('available', 'Sẵn sàng'),
            ('in_use', 'Đang sử dụng'),
        ],
        string='Trạng thái',
        default='available'
    )
    is_meeting_device = fields.Boolean(
        string="Thiết bị phòng họp",
        default=False
    )


    # ===============================
    # TỰ ĐỘNG GHI LỊCH SỬ
    # ===============================
    def write(self, vals):
        for asset in self:
            old_employee = asset.assigned_employee_id
            new_employee_id = vals.get('assigned_employee_id')

            if new_employee_id != old_employee.id:
                current_history = self.env['asset.history'].search([
                    ('asset_id', '=', asset.id),
                    ('status', '=', 'using')
                ], limit=1)

                if current_history:
                    current_history.write({
                        'end_date': date.today(),
                        'status': 'returned'
                    })

                if new_employee_id:
                    self.env['asset.history'].create({
                        'asset_id': asset.id,
                        'employee_id': new_employee_id,
                        'start_date': date.today(),
                        'status': 'using'
                    })

                vals['status'] = 'in_use' if new_employee_id else 'available'

        return super().write(vals)

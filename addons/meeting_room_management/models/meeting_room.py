from odoo import models, fields

class MeetingRoom(models.Model):
    _name = 'meeting.room'
    _description = 'Phòng họp'
    _order = 'name'

    name = fields.Char(
        string='Tên phòng',
        required=True
    )

    code = fields.Char(string='Mã phòng')

    capacity = fields.Integer(string='Sức chứa')

    # Nếu bạn muốn phòng thuộc vị trí tài sản thì giữ,
    # còn nếu muốn độc lập hoàn toàn thì có thể bỏ.
    location_id = fields.Many2one(
        'asset.location',
        string='Vị trí'
    )

    # Thiết bị lấy từ asset.asset (ERP chuẩn)
    device_ids = fields.Many2many(
        'asset.asset',
        string='Thiết bị trong phòng',
        domain=[('is_meeting_device', '=', True)]
    )

    note = fields.Text(string='Ghi chú')
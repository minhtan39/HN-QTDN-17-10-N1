from odoo import models, fields, api
from odoo.exceptions import ValidationError
from datetime import datetime

class ChamCong(models.Model):
    _name = 'cham_cong'
    _description = 'Bảng chấm công'
    _rec_name = 'ma_cham_cong'
    _order = 'ngay desc'

    ma_cham_cong = fields.Char(
        "Mã chấm công",
        required=True
    )

    nhan_vien_id = fields.Many2one(
        'nhan_vien',
        string='Nhân viên',
        required=True
    )

    ngay = fields.Date(
        "Ngày",
        default=fields.Date.today
    )

    gio_vao = fields.Datetime("Giờ vào")
    gio_ra = fields.Datetime("Giờ ra")

    tong_so_gio_lam = fields.Float(
        "Tổng số giờ làm",
        compute="_compute_tong_so_gio_lam",
        store=True
    )

    gio_ot = fields.Float(
        "Giờ OT",
        compute="_compute_gio_ot",
        store=True
    )

    trang_thai = fields.Selection(
        [
            ('di_lam', 'Đi làm'),
            ('nghi', 'Nghỉ'),
            ('tre', 'Đi trễ')
        ],
        string="Trạng thái",
        default='di_lam'
    )
    # ================== COMPUTE ==================

    @api.depends("gio_vao", "gio_ra")
    def _compute_tong_so_gio_lam(self):
        for record in self:
            if record.gio_vao and record.gio_ra:
                khoang_thoi_gian = record.gio_ra - record.gio_vao
                record.tong_so_gio_lam = khoang_thoi_gian.total_seconds() / 3600
            else:
                record.tong_so_gio_lam = 0

    @api.depends("tong_so_gio_lam")
    def _compute_gio_ot(self):
        for record in self:
            if record.tong_so_gio_lam > 8:
                record.gio_ot = record.tong_so_gio_lam - 8
            else:
                record.gio_ot = 0

    # ================== CONSTRAINS ==================

    @api.constrains("gio_vao", "gio_ra")
    def _check_gio_hop_le(self):
        for record in self:
            if record.gio_vao and record.gio_ra:
                if record.gio_ra < record.gio_vao:
                    raise ValidationError("Giờ ra không được nhỏ hơn giờ vào")

    # ================== ONCHANGE ==================

    @api.onchange("gio_vao")
    def _onchange_gio_vao(self):
        for record in self:
            if record.gio_vao:
                if record.gio_vao.hour > 8:
                    record.trang_thai = 'tre'
                else:
                    record.trang_thai = 'di_lam'

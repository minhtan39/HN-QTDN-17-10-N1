from odoo import models, fields, api
from odoo.exceptions import ValidationError


class AssetLocation(models.Model):
    _name = 'asset.location'
    _description = 'Vị trí tài sản'
    _order = 'name'

    name = fields.Char(
        string='Tên vị trí',
        required=True
    )

    code = fields.Char(
        string='Mã vị trí'
    )

    parent_id = fields.Many2one(
        'asset.location',
        string='Vị trí cha'
    )

    child_ids = fields.One2many(
        'asset.location',
        'parent_id',
        string='Vị trí con'
    )

    is_default = fields.Boolean(
        string='Vị trí mặc định',
        help='Tài sản sẽ quay về vị trí này khi trả'
    )

    note = fields.Text(
        string='Ghi chú'
    )

    # =========================
    # CHỈ CHO PHÉP 1 VỊ TRÍ MẶC ĐỊNH
    # =========================
    @api.constrains('is_default')
    def _check_only_one_default(self):
        for record in self:
            if record.is_default:
                others = self.search([
                    ('is_default', '=', True),
                    ('id', '!=', record.id)
                ])
                if others:
                    raise ValidationError(
                        "Chỉ được phép tồn tại một vị trí mặc định."
                    )

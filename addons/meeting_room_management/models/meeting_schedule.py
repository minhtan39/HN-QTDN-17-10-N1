from odoo import models, fields, api
from odoo.exceptions import ValidationError


class MeetingSchedule(models.Model):
    _name = 'meeting.schedule'
    _description = 'Lịch sử dụng phòng họp'
    _order = 'start_datetime desc'

    meeting_room_id = fields.Many2one(
        'meeting.room',
        string='Phòng họp',
        required=True
    )

    organizer_id = fields.Many2one(
        'hr.employee',
        string='Người phụ trách',
        required=True
    )

    start_datetime = fields.Datetime(
        string='Thời gian bắt đầu',
        required=True
    )

    end_datetime = fields.Datetime(
        string='Thời gian kết thúc',
        required=True
    )

    participant_ids = fields.Many2many(
        'hr.employee',
        string='Thành phần tham gia'
    )

    # ✅ FIX DOMAIN CHUẨN
    device_ids = fields.Many2many(
        'asset.asset',
        string='Thiết bị sử dụng',
        domain="[('is_meeting_device','=',True)]"
    )

    state = fields.Selection(
        [
            ('draft', 'Dự kiến'),
            ('confirmed', 'Đã xác nhận'),
            ('done', 'Hoàn thành'),
            ('cancel', 'Hủy'),
        ],
        string='Trạng thái',
        default='draft'
    )

    note = fields.Text(string='Ghi chú')

    # =========================
    # FILTER DEVICE THEO PHÒNG
    # =========================
    @api.onchange('meeting_room_id')
    def _onchange_meeting_room(self):
        if self.meeting_room_id:
            return {
                'domain': {
                    'device_ids': [
                        ('id', 'in', self.meeting_room_id.device_ids.ids)
                    ]
                }
            }

    # =========================
    # VALIDATE THỜI GIAN
    # =========================
    @api.constrains('start_datetime', 'end_datetime')
    def _check_time(self):
        for record in self:
            if record.start_datetime >= record.end_datetime:
                raise ValidationError(
                    "Thời gian kết thúc phải lớn hơn thời gian bắt đầu."
                )

    # =========================
    # CHẶN TRÙNG PHÒNG
    # =========================
    @api.constrains('meeting_room_id', 'start_datetime', 'end_datetime', 'state')
    def _check_meeting_room_overlap(self):
        for record in self:
            if record.state not in ('confirmed', 'done'):
                continue

            domain = [
                ('id', '!=', record.id),
                ('meeting_room_id', '=', record.meeting_room_id.id),
                ('state', 'in', ('confirmed', 'done')),
                ('start_datetime', '<', record.end_datetime),
                ('end_datetime', '>', record.start_datetime),
            ]

            if self.search(domain, limit=1):
                raise ValidationError(
                    "Phòng họp đã được đặt trong khoảng thời gian này."
                )

    # =========================
    # CHECK XUNG ĐỘT THIẾT BỊ
    # =========================
    @api.constrains('device_ids', 'start_datetime', 'end_datetime', 'state')
    def _check_device_conflict(self):
        for record in self:
            if not record.device_ids or record.state not in ('confirmed', 'done'):
                continue

            domain = [
                ('id', '!=', record.id),
                ('state', 'in', ('confirmed', 'done')),
                ('start_datetime', '<', record.end_datetime),
                ('end_datetime', '>', record.start_datetime),
                ('device_ids', 'in', record.device_ids.ids),
            ]

            if self.search(domain, limit=1):
                raise ValidationError(
                    "Thiết bị đang được sử dụng trong lịch họp khác."
                )

    # =========================
    # CHECK SỨC CHỨA
    # =========================
    @api.constrains('participant_ids', 'meeting_room_id', 'state')
    def _check_room_capacity(self):
        for record in self:
            if record.state != 'confirmed':
                continue

            if not record.meeting_room_id or not record.meeting_room_id.capacity:
                continue

            if len(record.participant_ids) > record.meeting_room_id.capacity:
                raise ValidationError(
                    f"Phòng '{record.meeting_room_id.name}' "
                    f"chỉ chứa tối đa {record.meeting_room_id.capacity} người."
                )

    # =========================
    # AI GỢI Ý PHÒNG
    # =========================
    def action_ai_suggest_room(self):
        for record in self:

            if not record.participant_ids:
                raise ValidationError(
                    "Vui lòng chọn thành phần tham gia trước."
                )

            participant_count = len(record.participant_ids)

            rooms = self.env['meeting.room'].search([
                ('capacity', '>=', participant_count)
            ])

            suitable_rooms = []

            for room in rooms:

                domain = [
                    ('meeting_room_id', '=', room.id),
                    ('state', 'in', ('confirmed', 'done')),
                    ('start_datetime', '<', record.end_datetime),
                    ('end_datetime', '>', record.start_datetime),
                ]

                conflict = self.search(domain, limit=1)

                if not conflict:
                    score = room.capacity - participant_count
                    suitable_rooms.append((room, score))

            if not suitable_rooms:
                raise ValidationError(
                    "Không có phòng phù hợp trong thời gian này."
                )

            suitable_rooms.sort(key=lambda x: x[1])
            record.meeting_room_id = suitable_rooms[0][0].id

    # =========================
    # ACTION
    # =========================
    def action_confirm(self):
        for record in self:
            record.state = 'confirmed'

    def action_done(self):
        for record in self:
            record.state = 'done'

    def action_cancel(self):
        for record in self:
            record.state = 'cancel'
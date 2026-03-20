{
    'name': 'Meeting Room Management',
    'version': '1.0',
    'summary': 'Quản lý phòng họp',
    'category': 'Business',
    'author': 'Your Team',
    'depends': ['hr', 'asset_management'],

    'data': [
        'security/ir.model.access.csv',

        # VIEW phải load trước
        'views/meeting_room_views.xml',
        'views/meeting_schedule_views.xml',

        # MENU luôn để cuối
        'views/menu.xml',
    ],

    'installable': True,
    'application': True,
}
{
    'name': 'Asset Management',
    'version': '1.0',
    'summary': 'Quản lý tài sản, kho và tồn kho',
    'category': 'Human Resources',
    'depends': ['hr'],
    'data': [
'security/ir.model.access.csv',

    'views/asset_location_views.xml',
    'views/asset_category_views.xml',

    'views/asset_history_views.xml',
    'views/asset_menu.xml',

    ],
    'application': True,
}

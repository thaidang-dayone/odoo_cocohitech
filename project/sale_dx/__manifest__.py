{
    'name': 'Sale DX',
    'version': '1.0',
    'summary': 'Custom sale module for Cocohitech DX',
    'description': 'This module provides custom contact management features for Cocohitech DX.',
    'author': 'thaidt',
    'website': 'http://www.dayoneteams.com',
    'category': 'Sales',
    'depends': ['sale_management', 'contact_dx'],
    'data': [
        'views/sale_order_views.xml',
        'views/partner_views.xml',
        'security/ir.model.access.csv',
        ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
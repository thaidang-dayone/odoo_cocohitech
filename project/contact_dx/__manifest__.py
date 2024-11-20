{
    'name': 'Contact DX',
    'version': '1.0',
    'summary': 'Custom contact module for Cocohitech DX',
    'description': 'This module provides custom contact management features for Cocohitech DX.',
    'author': 'thaidt',
    'website': 'http://www.dayoneteams.com',
    'category': 'Contacts',
    'depends': ['contacts'],
    'data': [
        'security/ir.model.access.csv',
        'views/res_partner_views.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
{
    'name': 'CRM DX',
    'version': '1.0',
    'summary': 'Custom CRM module for Cocohitech DX',
    'description': 'This module provides custom CRM management features for Cocohitech DX.',
    'author': 'thaidt',
    'website': 'http://www.dayoneteams.com',
    'category': 'CRM',
    'depends': ['crm'],
    'data': [
        'views/crm_lead_view.xml',
        'views/sale_order_view.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
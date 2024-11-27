{
    'name': 'Sale DX',
    'version': '1.0',
    'summary': 'Custom sale module for Cocohitech DX',
    'description': 'This module provides custom contact management features for Cocohitech DX.',
    'author': 'thaidt',
    'website': 'http://www.dayoneteams.com',
    'category': 'Sales',
    'depends': [
        'sale', 
        'contact_dx', 
        'crm'
        ],
    'data': [
        'views/sale_order_views.xml',
        'views/document_digital_view.xml',
        'views/crm_lead_view.xml',
        'security/ir.model.access.csv',
        'data/product_data.xml',
        ],
    'installable': True,
    'application': True,
    'auto_install': False,
    'assets': {
        'web.assets_backend': [
            'sale_dx/static/src/picker/limit_color_picker.js',
            'sale_dx/static/src/picker/limit_color_picker.xml',
            'sale_dx/static/src/picker/limit_color_picker.scss',
            
        ],
    },
}
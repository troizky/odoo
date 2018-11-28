# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'POS Customer Display',
    'version': '1.0',
    'category': 'Point Of Sale',
    'summary': 'Customer Display device for point of sale',
    'description': """
        Customer display device for point of sale
    """,
    'depends': ['point_of_sale'],
    'data': [
        'views/pos_customer_display.xml',
        'views/customer_display_view.xml',
        ],
    'demo': ['demo/pos_customer_display_demo.xml'],
    'installable': True,
    'website': 'https://www.odoo.com/page/point-of-sale',
}

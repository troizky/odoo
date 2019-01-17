# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': "WNJI additional functions for point of sale",
    'category': 'Point of Sale',
    'version': '1.0',
    'sequence': 6,
    'summary': 'Tools for using WNJI device for point of sale',
    'description': """
        WNJI device for point of sale
        some useful stuff
""",
    'depends': ['point_of_sale'],
    'data': [
        'views/pos_order_view.xml',
        'views/templates.xml',
    ],
    'qweb': [
        'static/src/xml/test_wnji.xml',
    ],
    'installable': True,
    'application': True,
}
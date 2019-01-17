# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'WNJI-003f Fiscal Registrator Hardware Driver',
    'category': 'Point of Sale',
    'sequence': 6,
    'summary': 'Hardware Driver for WNJI-003f Fiscal Registrator',
    'website': 'https://www.odoo.com/page/point-of-sale',
    'description': """
WNJI-003f Fiscal Registrator Hardware Driver
================================

This module allows the web client to access a remotely installed wnji-003f,
and is used by the posbox to provide fiscal registrator support to the
point of sale module. 

""",
    'depends': ['hw_proxy'],
    'installable': True,
}

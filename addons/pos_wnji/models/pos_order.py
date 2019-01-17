# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api
from . import hw_proxy_sender


import pprint

class PosOrder(models.Model):
    _name = 'pos.order'
    _inherit = ['pos.order']

    import logging
    _logger = logging.getLogger(__name__)
    _logger.info('dzm: {}'.format('\nPOS ORDER HAS BEEN OVERWRITTEN'*3))

    order_type = fields.Char(string='Order Type', required=True, readonly=True, copy=False, default='Income')


    # test function
    def do_smh(self):

        proxy_url = self.env['pos.config'].browse(1).proxy_ip # TODO : fix hardcoded config id
        path = '/hw_proxy/x_report_test'

        data = {
            "jsonrpc": "2.0",
            "method": "call",
            "params": {
                "cashier": self.env.user.name,
            },
            "id": 1337,
        }

        _logger.info(data)

        hw_proxy_sender.send(url=proxy_url+path, data=data, method='POST')


    # sending paid receipt to wnji device from web

    @api.multi
    def action_pos_order_paid(self):
        if not self.test_paid():
            raise UserError(_("Order is not paid."))
        self.write({'state': 'paid'}) # TODO should we print receipt first and only then close the order in odoo or not?

        import logging
        _logger = logging.getLogger(__name__)
        _logger.info('dzm: {}'.format('\n OWERRITEN action_pos_order_paid METHOD WAS CALLED'*3))

        proxy_url = self.env['pos.config'].browse(1).proxy_ip # TODO : fix hardcoded config id
        path = '/hw_proxy/print_wnji'

        #======================================================================
        # Generating JSON payload with all required order data

        json_receipt = {'lines': [], 'payments': []}
        json_receipt['cashier'] = self.env.user.name

        for line in self.lines.read(['display_name', 'price_unit', 'qty', 'discount']):
            json_receipt['lines'].append({
                'name': line['display_name'],
                'quantity': line['qty'],
                'price': line['price_unit'],
                'discount': line['discount'],
            })

        for payment in self.statement_ids.read(['amount', 'journal_id']):
            json_receipt['payments'].append({
                'type': payment['journal_id'][1],
                'amount': payment['amount'],
            })

        # ======================================================================

        json_message = {
            "jsonrpc": "2.0",
            "method": "call",
            "params": {
                "receipt": json_receipt,
            },
            "id": 13337
        }

        try:
            hw_proxy_sender.send(url=proxy_url+path, data=json_message, method='POST')
        except Exception as e:
            with open('D:/111.txt', 'a') as f:
                f.write(str(e))
                _logger.warning('\nEXCEPTION IN action_pos_order_paid, SOMETHING WENT WRONG\n')

        return self.create_picking()
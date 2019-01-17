# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api
from . import hw_proxy_sender


# sends "open shift" message on wnji fiscal registrator
# TODO : add "close shift" message

class PosSessionInherit(models.Model):
    _name = 'pos.session'
    _inherit = ['pos.session']

    import logging
    _logger = logging.getLogger(__name__)
    _logger.info('dzm: {}'.format('\nPosSession class HAS BEEN OVERWRITTEN'*3))

    @api.multi
    def action_pos_session_open(self):
        ret = super(PosSessionInherit, self).action_pos_session_open()

        proxy_url = self.env['pos.config'].browse(1).proxy_ip # TODO : fix hardcoded config id
        path = '/hw_proxy/open_shift'

        data = {
            "jsonrpc": "2.0",
            "method": "call",
            "params": {
                "cashier": self.env.user.name,
            },
            "id": 1337,
        }

        hw_proxy_sender.send(url=proxy_url+path, data=data, method='POST')

        return ret
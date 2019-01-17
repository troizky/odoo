# -*- coding: utf-8 -*-
from odoo import http

# class PosWnji(http.Controller):
#     @http.route('/pos_wnji/pos_wnji/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/pos_wnji/pos_wnji/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('pos_wnji.listing', {
#             'root': '/pos_wnji/pos_wnji',
#             'objects': http.request.env['pos_wnji.pos_wnji'].search([]),
#         })

#     @http.route('/pos_wnji/pos_wnji/objects/<model("pos_wnji.pos_wnji"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('pos_wnji.object', {
#             'object': obj
#         })
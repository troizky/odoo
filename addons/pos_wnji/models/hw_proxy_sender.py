# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import requests, pprint

# Sends message from web to proxy url of the device (probably can be done better)

def send(url, data, method):

    with requests.Session() as sender:
        if method=='GET':
            resp = sender.get(url=url)
        elif method=='POST':
            sender.headers = {'content-type': 'application/json'}
            resp = sender.post(url=url, json=data)
        else:
            pass

# TODO : cleanup response handling
    try:
        resp.raise_for_status()
        try:
            _resp = resp.json()
        except:
            _resp = resp.text
    except Exception as e:
        _resp = e
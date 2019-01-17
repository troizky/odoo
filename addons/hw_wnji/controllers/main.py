# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from __future__ import print_function
import logging
import subprocess
import time

try: 
    from .. wnji import *
except ImportError: 
    wnji = None

try:
    from queue import Queue
except ImportError:
    from Queue import Queue # pylint: disable=deprecated-module
from threading import Thread, Lock

from odoo import http, _
from odoo.addons.hw_proxy.controllers import main as hw_proxy

_logger = logging.getLogger(__name__)

from datetime import datetime
datetime.strptime('2012-01-01', '%Y-%m-%d')


class WNJIDriver(Thread):
    def __init__(self):
        Thread.__init__(self)
        self.queue = Queue()
        self.lock  = Lock()
        self.status = {'status':'connecting', 'messages':[]}

    def lockedstart(self):
        with self.lock:
            if not self.isAlive():
                self.daemon = True
                self.start()
    
    def get_wnji_fiscal_registrator(self):
        printer = wnji.Printer()
        state = printer.device_state()
        if state:
            self.set_status(
                'not connected',
                state,
            )
            return None
        else:
            self.set_status(
                'connected',
                "WNJI-003f is successfully connected to /def/ttyS3"
            )
            return printer

    def get_status(self):
        self.push_task('status')
        return self.status

    def set_status(self, status, message = None):
        _logger.info(status+' : '+ (message or 'no message'))
        if status == self.status['status']:
            if message != None and (len(self.status['messages']) == 0 or message != self.status['messages'][-1]):
                self.status['messages'].append(message)
        else:
            self.status['status'] = status
            if message:
                self.status['messages'] = [message]
            else:
                self.status['messages'] = []

        if status == 'error' and message:
            _logger.error('WNJI Error: %s', message)
        elif status == 'disconnected' and message:
            _logger.warning('WNJI Device Disconnected: %s', message)

    def run(self):
        printer = None
        if not wnji:
            _logger.error('WNJI cannot initialize, please verify system dependencies.')
            return
        while True:
            try:
                error = True
                timestamp, task, data = self.queue.get(True)

                printer = self.get_wnji_fiscal_registrator()

                if printer == None:
                    if task != 'status':
                        self.queue.put((timestamp,task,data))
                    error = False
                    time.sleep(5)
                    continue
                elif task == 'receipt': 
                    if timestamp >= time.time() - 1 * 60 * 60:
                        printer.open()
                        printer.text('smthng went wrong? rc 322')
                        printer.close()
                        # self.print_receipt_body(printer,data)
                elif task == 'wnji_receipt':
                    if timestamp >= time.time() - 1 * 60 * 60:
                        self.send_receipt_to_wnji(printer, data)
                elif task == 'x_report_test':
                    self.print_x_report(printer, data)
                elif task == 'close_shift':
                    self.close_shift(printer, data)
                elif task == 'open_shift':
                    self.open_shift(printer, data)
                elif task == 'x_report':
                    self.print_x_report(printer)
                elif task == 'raw_text':
                    self.print_raw_text(printer, data)
                elif task == 'cashbox':
                    if timestamp >= time.time() - 12:
                        self.open_cashbox()
                elif task == 'test':
                    printer.test()
                elif task == 'status':
                    pass
                error = False

                '''except NoDeviceError as e:
                print("No device found %s" % e)
            except HandleDeviceError as e:
                print("Impossible to handle the device due to previous error %s" % e)
            except TicketNotPrinted as e:
                print("The ticket does not seems to have been fully printed %s" % e)
            except NoStatusError as e:
                print("Impossible to get the status of the printer %s" % e)'''

            except Exception as e:
                self.set_status('error', 'error')
                print("===>")
                print(e)
                print("<===")
                _logger.exception(e)

            finally:
                if error:
                    self.queue.put((timestamp, task, data))
                if printer and printer.isOpen():
                    printer.close()

    def push_task(self,task, data = None):
        self.lockedstart()
        self.queue.put((time.time(),task,data))

    def open_cashbox(self):
        subprocess.call(['cdm','open'])

    def print_raw_text(self, printer, raw_text):
        try:
            printer.text(raw_text)
        except:
            raise

    def send_receipt_to_wnji(self, printer, receipt):
        try:
            printer.print_json_receipt(receipt)
        except:
            raise

    def open_shift(self, printer, cashier=''):
        printer.shift_start(cashier.encode('cp866'))

    def close_shift(self, printer, cashier=''):
        printer.z_report(cashier.encode('cp866'))

    def print_x_report(self, printer, cashier=''):
        try:
            if cashier:
                printer.x_report(cashier.encode('cp866'))
            else:
                printer.x_report()
        except:
            raise


driver = WNJIDriver()

hw_proxy.drivers['wnji'] = driver

class WNJIProxy(hw_proxy.Proxy):
   
    @http.route('/hw_proxy/print_receipt', type='json', auth='none', cors='*')
    def print_receipt(self, receipt):
        _logger.info('WNJI: PRINT RECEIPT') 
        driver.push_task('receipt', receipt)

    @http.route('/hw_proxy/print_wnji', type='json', auth='none', cors='*')
    def print_wnji(self, receipt):
        _logger.info('WNJI: PRINT RECEIPT') 
        driver.push_task('wnji_receipt',receipt)

    @http.route('/hw_proxy/x_report_test', type='json', auth='none', cors='*')
    def print_x_report_test(self, cashier):
        _logger.info('WNJI: PRINT X-REPORT')
        _logger.info(cashier)
        driver.push_task('x_report_test', cashier)

    @http.route('/hw_proxy/x_report', type='http', auth='none', cors='*')
    def print_x_report(self):
        _logger.info('WNJI: PRINT X-REPORT')
        driver.push_task('x_report')

    @http.route('/hw_proxy/print_sample', type='http', auth='none', cors='*')
    def print_sample(self):
        _logger.info('WNJI: Printing test check') 
        driver.push_task('test')

    @http.route('/hw_proxy/open_cashbox', type='json', auth='none', cors='*')
    def open_cashbox(self):
        _logger.info('WNJI: OPEN CASHBOX') 
        driver.push_task('cashbox')

    @http.route('/hw_proxy/open_shift', type='json', auth='none', cors='*')
    def open_fiscal_day(self, cashier):
        _logger.info('WNJI: OPEN SHIFT')
        driver.push_task('open_shift', cashier)

    @http.route('/hw_proxy/raw_text', type='json', auth='none', cors='*')
    def print_raw_text(self, raw_text):
        _logger.info('WNJI: PRINTING RAW TEXT')
        driver.push_task('raw_text', raw_text)

    @http.route('/hw_proxy/close_shift', type='json', auth='none', cors='*')
    def close_fiscal_day(self, cashier):
        _logger.info('WNJI: CLOSE SHIFT')
        driver.push_task('close_shift', cashier)

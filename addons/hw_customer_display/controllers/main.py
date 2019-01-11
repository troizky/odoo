# -*- encoding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import logging
import simplejson
import time
from threading import Thread, Lock
from Queue import Queue
from odoo.addons.hw_proxy.controllers import main as hw_proxy
from odoo import http
from odoo.tools.config import config

logger = logging.getLogger(__name__)

try:
    from serial import Serial
except (ImportError, IOError) as err:
    logger.error(err)


class CustomerDisplay(Thread):
    def __init__(self):
        Thread.__init__(self)
        self.queue = Queue()
        self.lock = Lock()
        self.status = {'status': 'connecting', 'messages': []}
        self.device_name = config.get(
            'customer_display_device_name', '/dev/ttyS4')
        self.device_rate = int(config.get(
            'customer_display_device_rate', 9600))
        self.device_timeout = int(config.get(
            'customer_display_device_timeout', 2))
        self.serial = False

    def get_status(self):
        self.push_task('status')
        return self.status

    def set_status(self, status, message=None):
        if status == self.status['status']:
            if message is not None and message != self.status['messages'][-1]:
                self.status['messages'].append(message)
        else:
            self.status['status'] = status
            if message:
                self.status['messages'] = [message]
            else:
                self.status['messages'] = []

        if status == 'error' and message:
            logger.error('Display Error: '+message)
        elif status == 'disconnected' and message:
            logger.warning('Disconnected Display: '+message)

    def lockedstart(self):
        with self.lock:
            if not self.isAlive():
                self.daemon = True
                self.start()

    def push_task(self, task, data=None):
        self.lockedstart()
        self.queue.put((time.time(), task, data))

    def move_cursor(self, col, row):
        cmd = '\x1B\x5B%c\x3B%c\x48' % (chr(0x30 + row), chr(0x30 + col))
        self.cmd_serial_write(cmd.encode(errors='ignore'))

    def display_text(self, lines):
        logger.debug(
            "Preparing to send the following lines to LCD: %s" % lines)
        # We don't check the number of rows/cols here, because it has already
        # been checked in the POS client in the JS code
        lines_ascii = []
        for line in lines:
            lines_ascii.append(line.encode('cp866', errors='ignore'))
        row = 0
        for dline in lines_ascii:
            row += 1
            self.move_cursor(1, row)
            self.serial_write(dline)

    def setup_customer_display(self):
        '''Set LCD cursor to off
        If your LCD has different setup instruction(s), you should
        inherit this function'''
        self.cmd_serial_write('\x1B\x52\x29'.encode(errors='ignore'))
        logger.debug('LCD cursor set to off')

    def clear_customer_display(self):
        '''If your LCD has different clearing instruction, you should inherit
        this function'''
        self.cmd_serial_write('\x1B\x5B\x32\x4A'.encode(errors='ignore'))
        logger.debug('Customer display cleared on port %s with baudrate %d' % (self.serial.port, self.serial.baudrate))

    def cmd_serial_write(self, command):
        '''If your LCD requires a prefix and/or suffix on all commands,
        you should inherit this function'''
        assert isinstance(command, str), 'command must be a string'
        self.serial_write(command)

    def serial_write(self, text):
        assert isinstance(text, str), 'text must be a string'
        self.serial.write(text)

    def send_text_customer_display(self, text_to_display):
        '''This function sends the data to the serial/usb port.
        We open and close the serial connection on every message display.
        Why ?
        1. Because it is not a problem for the customer display
        2. Because it is not a problem for performance, according to my tests
        3. Because it allows recovery on errors : you can unplug/replug the
        customer display and it will work again on the next message without
        problem
        '''
        lines = simplejson.loads(text_to_display)
        assert isinstance(lines, list), 'lines_list should be a list'
        try:
            logger.debug(
                'Opening serial port %s for customer display with baudrate %d'
                % (self.device_name, self.device_rate))
            self.serial = Serial()
            self.serial.port = self.device_name
            self.serial.baudrate = self.device_rate
            self.serial.timeout = self.device_timeout
            self.serial.bytesize = 8
            self.serial.parity = 'O'
            self.serial.stopbits = 1
            self.serial.xonxoff = False
            self.serial.rtscts = False
            self.serial.dsrdtr = False
            self.serial.writeTimeout = 0
            self.serial.open()
            logger.debug('serial.is_open = %s' % self.serial.isOpen())
            self.setup_customer_display()
            self.clear_customer_display()
            self.display_text(lines)
        except Exception, e:
            logger.error('Exception in serial connection: %s' % str(e))
        finally:
            if self.serial:
                logger.debug('Closing serial port for customer display')
                time.sleep(0.5)
                self.serial.flushInput()
                self.serial.flushOutput()
                self.serial.close()

    def run(self):
        while True:
            try:
                timestamp, task, data = self.queue.get(True)
                if task == 'display':
                    self.send_text_customer_display(data)
                elif task == 'status':
                    pass
            except Exception as e:
                self.set_status('error', str(e))


customer_display_thread = CustomerDisplay()

hw_proxy.drivers['customer_display'] = customer_display_thread


class CustomerDisplayDriver(hw_proxy.Proxy):
    @http.route(
        '/hw_proxy/send_text_customer_display', type='json', auth='none',
        cors='*')
    def send_text_customer_display(self, text_to_display):
        logger.info(
            'LCD: Call send_text_customer_display with text=%s',
            text_to_display)
        customer_display_thread.push_task('display', text_to_display)

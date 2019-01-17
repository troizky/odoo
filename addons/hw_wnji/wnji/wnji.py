# -*- coding: utf-8 -*-

import serial
import sys
import os
import time
from .constants import *
from random import randint

# Decorator for send/receive

def send(command, timeout=3):
    def decorator(func):
        def wrapper(self, *args, **kwargs):

            if self.silent:
                self._original_stdout = sys.stdout
                sys.stdout = open(os.devnull, 'w')

            print('-=-=- start | function {} | -=-=-'.format(func.__name__))
            print(args, kwargs)
            args = func(self, *args, **kwargs)
            response = self.send_command(command, timeout, *args)
            print('-=-=-  end | function {} | -=-=-'.format(func.__name__))

            if self.silent:
                sys.stdout.close()
                sys.stdout = self._original_stdout         
            
            if response[0] == '00':
                return response
            else:
                raise Exception('WNJI protocol error: '+PRINTER_RESPONSE_ERROR_CODES[response[0]])
        return wrapper
    return decorator

def csum(x):
    try:
        sum = ord(x[1]) # STX is excluded from checksum
        for i in xrange(2, len(x)):
            sum ^= ord(x[i])
        return sum
    except Exception as e:
        print("Wrong argument for csum: " + str(e))

def as_hex(x):
    try:
        ah = hex(x)
        return '0'+ah[-1] if ah[-2] == 'x' else ah[-2:]
    except Exception as e:
        print("Wrong argument for as_hex: " + str(e))


class Printer(serial.Serial):

    def __init__(self, device='/dev/ttyS3', baudrate=115200, silent=False):
        super(Printer, self).__init__()
        self.port = device
        self.baudrate = baudrate
        self.timeout = 3
        self.bytesize = serial.EIGHTBITS
        self.parity = serial.PARITY_NONE
        self.stopbits = serial.STOPBITS_ONE
        self.xonxoff = False
        self.rtscts = True
        self.dsrdtr = False
        self.writeTimeout = 3
        self.silent = silent
        self.open()

    # Sends WNJI command to the device
    def send_command(self, command, timeout=3, *args):
        print((' req:{:>3};{:>3}'+'; {}'*len(args)).format(command, '', *args))
        package_name = chr(randint(32, 240))
        msg = STX + PASSWORD + package_name + command + (('{}'+FS)*len(args)).format(*args) + ETX
        msg = msg + as_hex(csum(msg)).upper()
        self.write(msg)
        return self.read_response(package_name, timeout)

    # Reads WNJI response from the device
    def read_response(self, package_name='', timeout=3):
        start_time = time.time()
        while time.time()<(start_time+timeout):
            while not self.inWaiting():
                time.sleep(.1) # TODO improve this ugly abomination
                continue
            else:
                time.sleep(.2)
                bytesToRead = self.inWaiting()
                resp = self.read(bytesToRead)
                print("Raw response:\n{}".format(resp))
                print('got response in {:>5.2} seconds'.format(time.time()-start_time))
                if resp:
                    resp_a = [x.split('\x03')[0] for x in resp.split('\x02')[1:]]
                    for msg in resp_a:
                        print(('resp:{:>3};{:>3}'+'; {}'*msg.count(FS)).format(msg[1:3], msg[3:5], *tuple(msg[5:].split(FS)[:-1])))
                        if msg[0]==package_name:
                            return [msg[3:5]]+msg[5:].split(FS)[:-1]
                print('We\'ve got response for an incorrect package, we\'re deeply sorry (not sorry)')
                break
        return ['42', 'The printer hasn\'t responded in {} seconds, check connection.'.format(timeout)]

    # WNJI device status check
    def device_state(self):
        rc = int(self.send_command(DEV_STATE_REQ)[1])
        resp = []
        i = 0
        while rc:
            if rc&1:
                resp.append(DEVICE_STATE_BITMAP[i])
            rc>>=1
            i+=1
        return ', '.join(resp)

    def status_two(self):
        """
        :return: bitmask, bitmask
        
        0 The “Beginning of work” command was missed
        1 Non-fiscal mode
        2 A shift is open
        3 A shift is open more than 24 hours
        4 The FA is connected
        5 The FA archive is closed

        0 Document is closed
        1 Non-fiscal document
        2 Sale receipt (Income receipt)
        3 Return receipt (Income refund receipt)
        4 Cash-In
        5 Cash-out
        6 Outcome receipt
        7 Outcome refund receipt
        8 Correction receipt
        """
        self.send_command(STATUS_2_REQ)

    @send(SHIFT_START)
    def shift_start(self, *args):
        return args

    @send(X_REPORT, 60)
    def x_report(self, *args):
        return args

    @send(Z_REPORT, 60)
    def z_report(self, *args):
        return args

    @send(OPEN_DOC)
    def open_doc(self, doc_type=2, num_depot=1, cashier='sorok sed\'moi'):
        return [doc_type, num_depot, cashier]

    @send(CLOSE_DOC)
    def close_doc(self, *args):
        return args

    @send(CANCEL_DOC)
    def cancel_doc(self, *args):
        return args

    @send(ADD_ITEM)
    def add_item(self, *args):
        return args

    @send(SUB_TOTAL)
    def sub_total(self, *args):
        return args

    @send(ADD_PAYMENT)
    def add_payment(self, *args):
        return args

    @send(PRINT_TEXT)
    def text_string(self, *args):
        return args

    def text(self, text, mode=0):
        for line in text.split('\n'):
            self.text_string(line.decode('utf8').encode('cp866'), mode)

    # Parsing json receipt into valid receipt for WNJI device
    def print_json_receipt(self, receipt):

        sold_items = []
        refunded_items = []
        refunded_amount = 0
        for line in receipt['lines']:
            if line['quantity'] < 0:
                refunded_items+=[line]
                refunded_amount+=-1.0*line['quantity']*line['price']
            if line['quantity'] > 0:
                if line['price'] >= 0:
                    sold_items+=[line]
        payments = [{'type': 'Refunded cash', 'amount': refunded_amount}] if refunded_amount else []
        payments+=receipt['payments']

        print('-=-=- start | receipt printing -=-=-')

        if refunded_items:
            try:        
                self.open_doc(doc_type=3, cashier=receipt['cashier'].encode('cp866'))
                for item in refunded_items:
                    self.add_item(
                        item['name'].encode('cp866'),
                        '',
                        item['quantity'],
                        item['price']*(100.0-item['discount'])/100,
                        0,
                        0,
                        1,
                        4,
                        1,
                    )
                self.sub_total()
                self.add_payment(
                    0,
                    refunded_amount,
                    'Moneyback for refunded_items',
                )
            except:
                self.cancel_doc()
                raise
            else:
                self.close_doc(FULL_CUT)

        if sold_items:
            try:
                self.open_doc(cashier=receipt['cashier'].encode('cp866'))
                for item in sold_items:
                    self.add_item(
                        item['name'].encode('cp866'),  
                        '',
                        item['quantity'],
                        item['price']*(100.0-item['discount'])/100,
                        0,
                        0,
                        1,
                        4,
                        1
                    )
                self.sub_total()
                for payment in payments:
                    self.add_payment(
                        0,
                        payment['amount'],
                        'Paying with {}'.format(payment['type']),
                    )
            except:
                self.cancel_doc()
                raise
            else:
                self.close_doc(FULL_CUT)

        print('-=-=-  end  | receipt printing -=-=-')






    def test(self):
#        self.open()
        self.open_doc()
        self.add_item('Тестовый продукт'.decode('utf8').encode('cp866'), '', 1.3, 14, 0, 0, 1)
        self.add_item('Продукт тестовый'.decode('utf8').encode('cp866'), '', 4, 3.6, 0, 0, 1)
        self.send_command('44')
        self.send_command('47', 3, 0, 100, 'йохохо, and a bottle of rrrum'.decode('utf8').encode('cp866'))
        self.send_command('31', 3, 1)
#        self.close()

    def long_long_test(self):
        t = time.time()
#        self.open()
        self.open_doc()
        names = ['биочип','барсук','гонион','бодяга','амичит','байпас','гагеит','вноска','гарман','бензой','бусидо','дарбар','виппер','берилл','алария','бузила','банива','гэбист','гаврош','деанол','азития','восеец','бодряк','ведьма','гребец','гратис','ацидит','бракёр','бистро','бальяж']
        for i in xrange(0,6):
            self.add_item(names[i].decode('utf8').encode('cp866'), '', randint(1,5), randint(500,10000)/100.0, i, i, i)
        self.send_command('44')
        self.send_command('47', 0, 10000, 'старый добрый кэшинский'.decode('utf8').encode('cp866'))
        self.send_command('31', 1)
#        self.close()
        print('30 items check printed in {:>5.2} seconds'.format(time.time()-t))

def full_test():
    try:
        shift_opened = False
        o = Printer(silent=True)
        print('Printer has been initialized.')
        try:
            o.shift_start()
            print('New fiscal day has been started.')
        except:
            print('A fiscal day is already started.')
            shift_opened = True
        try:
            o.test()
        except:
            print('The current fiscal day has been opened for more than 24 hours.')
            o.z_report()
            print('The fiscal day has been closed.')
            o.shift_start()
            print('New fiscal day has been started.')
            o.test()
        print('A new receipt has been printed.')
        if not shift_opened:
            o.z_report()
            print('The fiscal day has been closed.')
        o.close()
    except Exception as e:
        print('Something went wrong: {}'.format(e))
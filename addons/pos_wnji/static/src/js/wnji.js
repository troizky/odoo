odoo.define('pos_wnji', function(require) {
    "use strict";

    var config = require('web.config');
    var core = require('web.core');
    var _t = core._t;
    var chrome = require('point_of_sale.chrome');
    var devices = require('point_of_sale.devices');  
    var screens = require('point_of_sale.screens');
    var gui = require('point_of_sale.gui');


// adding wnji-003f fiscal registrator as proxy device

    devices.ProxyDevice.include({
        print_wnji: function(receipt){
            var self = this;
            if(receipt){
                this.receipt_queue.push(receipt);
            }
            function send_printing_job(){
                if (self.receipt_queue.length > 0){
                    var r = self.receipt_queue.shift();
                    self.message('print_wnji',{ receipt: r },{ timeout: 5000 })
                        .then(function(){
                            send_printing_job();
                        },function(error){
                            if (error) {
                                self.pos.gui.show_popup('error-traceback',{
                                    'title': _t('Printing via WNJI Error: ') + error.data.message,
                                    'body':  error.data.debug,
                                });
                                return;
                            }
                            self.receipt_queue.unshift(r);
                        });
                }
            }
            send_printing_job();
        },
        print_raw: function(text){
            this.message('raw_text',{ raw_text: text },{ timeout: 5000 })
        },

    });

// status of wnji

    chrome.ProxyStatusWidget.include({
        set_smart_status: function(status){
            if(status.status === 'connected'){
                var warning = false;
                var msg = '';
                if(this.pos.config.iface_scan_via_proxy){
                    var scanner = status.drivers.scanner ? status.drivers.scanner.status : false;
                    if( scanner != 'connected' && scanner != 'connecting'){
                        warning = true;
                        msg += _t('Scanner');
                    }
                }
                if( this.pos.config.iface_print_via_proxy ||
                    this.pos.config.iface_cashdrawer ){
                    var printer = status.drivers.escpos ? status.drivers.escpos.status : false;
                    var printer = status.drivers.wnji ? status.drivers.wnji.status : false;
                    if( printer != 'connected' && printer != 'connecting'){
                        warning = true;
                        msg = msg ? msg + ' & ' : msg;
                        msg += _t('Printer');
                    }
                }
                if( this.pos.config.iface_electronic_scale ){
                    var scale = status.drivers.scale ? status.drivers.scale.status : false;
                    if( scale != 'connected' && scale != 'connecting' ){
                        warning = true;
                        msg = msg ? msg + ' & ' : msg;
                        msg += _t('Scale');
                    }
                }

                msg = msg ? msg + ' ' + _t('Offline') : msg;
                this.set_status(warning ? 'warning' : 'connected', msg);
            }else{
                this.set_status(status.status,'');
            }
        },
    });

// wnji print function

    screens.ReceiptScreenWidget.include({
        print_wnji: function() {
            var order_json = {'lines':[], 'payments':[]};
            order_json['cashier'] = this.pos.get_order().pos.get_cashier().name
            this.pos.get_order().get_orderlines().forEach(function(line){
                order_json['lines'].push({
                    'name': line.product.display_name,
                    'quantity': line.quantity,
                    'price': line.price,
                    'discount': line.discount,
                });
            });
            this.pos.get_order().get_paymentlines().forEach(function(payment){
                order_json['payments'].push({
                    'type': payment.name,
                    'amount': payment.amount,
                });
            });
            console.log(order_json);
            this.pos.proxy.print_wnji(order_json);
            this.pos.get_order()._printed = true;
        },
        print: function() {
            var self = this;

            if (!this.pos.config.iface_print_via_proxy) { // browser (html) printing
                this.lock_screen(true);
                setTimeout(function(){
                    self.lock_screen(false);
                }, 1000);
                this.print_web();
            } else {    // proxy (xml) printing
                this.print_wnji();
                this.lock_screen(false);
            }
        },

    });
});

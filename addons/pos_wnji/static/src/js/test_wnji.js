odoo.define('wnji.test_wnji', function (require) {
"use strict";
var core = require('web.core');
var screens = require('point_of_sale.screens');
var gui = require('point_of_sale.gui');
var config = require('web.config');
var core = require('web.core');
var _t = core._t;
var chrome = require('point_of_sale.chrome');
var devices = require('point_of_sale.devices');
var screens = require('point_of_sale.screens');
var QWeb = core.qweb;

// This whole script just adds additional buttons to ActionButtonWidget for testing purposes

var PrintButton = screens.ActionButtonWidget.extend({
    template: 'print_button',

    button_click: function(){
        var self = this;
        self.print_raw_text();
    },

    print_raw_text: function() {
        if(this.pos.config.iface_print_via_proxy){
            var temp_str = prompt("Please enter your name:", "Harry Potter");
            this.pos.proxy.print_raw(temp_str);
        } else {
            this.gui.show_popup('error',{
                'title': 'The printer isn\'t available.',
                'body':  'Use the button on the left to turn it on, baka!',
        });
        }
    },

});

var PopupButton = screens.ActionButtonWidget.extend({
    template: 'popup_button',

    button_click: function(){
        var self = this;
        self.popup_sample();
    },

    popup_sample: function() {
        this.gui.show_popup('error',{
            'title': 'test',
            'body':  'huest',
        });
    },

});

var TurnOffButton = screens.ActionButtonWidget.extend({
    template: 'off_button',

    init: function(parent){
        this._super(parent);
        console.log(this);
    },

    start: function(){
        console.log(this);
        if(this.pos.config.iface_print_via_proxy){
            this.pos.config.iface_print_via_proxy = !this.pos.config.iface_print_via_proxy;
        };
    },

    button_click: function(){
        console.log(this);
        var self = this;
        self.turn_off();
    },

    turn_off: function() {
        console.log(this);
        console.log(this.pos.config.iface_print_via_proxy);
        this.pos.config.iface_print_via_proxy = !this.pos.config.iface_print_via_proxy;
        console.log(this.pos.config.iface_print_via_proxy);
    },

});

screens.define_action_button({
    'name': 'gdfghfg',
    'widget': TurnOffButton,
});

screens.define_action_button({
    'name': 'dfsggfddfgdff',
    'widget': PopupButton,
});

screens.define_action_button({
    'name': 'dfsgdfgdff',
    'widget': PrintButton,
});

});
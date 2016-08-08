# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from statemachine import _Statemachine


class Windows8_1StateMachine(_Statemachine):
    def __init__(self, params):
        _Statemachine.__init__(self, params)

    def _list_running(self):
        return super(Windows8_1StateMachine, self)._list_running()

    def _list_arp_table(self):
        return super(Windows8_1StateMachine, self)._list_arp_table()

    def _list_route_table(self):
        return super(Windows8_1StateMachine, self)._list_route_table()

    def _list_sockets_network(self):
        return super(Windows8_1StateMachine, self)._list_sockets_network()

    def _list_sockets_services(self):
        return super(Windows8_1StateMachine, self)._list_services()



    def list_running_proccess(self):
        super(Windows8_1StateMachine, self)._list_running_process(self._list_running())

    def list_arp_table(self):
        super(Windows8_1StateMachine, self)._csv_list_arp_table(self._list_arp_table())

    def list_route_table(self):
        super(Windows8_1StateMachine, self)._csv_list_route_table(self._list_route_table())

    def list_sockets_networks(self):
        super(Windows8_1StateMachine, self)._csv_list_sockets_network(self._list_sockets_network())

    def list_services(self):
        super(Windows8_1StateMachine, self)._csv_list_services(self._list_services())

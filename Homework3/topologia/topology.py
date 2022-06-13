#!/usr/bin/python

from mininet.topo import Topo

class TwoWayTopology(Topo):
    def __init__(self):
        Topo.__init__(self)
        # Switches
        s1 = self.addSwitch('s1', dpid = '1')
        s2 = self.addSwitch('s2', dpid = '2')
        s3 = self.addSwitch('s3', dpid = '3')
        s4 = self.addSwitch('s4', dpid = '4')
        # Hosts
        h1 = self.addHost('h1', mac = '00:00:00:00:00:01')
        h2 = self.addHost('h2', mac = '00:00:00:00:00:02')
        h3 = self.addHost('h3', mac = '00:00:00:00:00:03')
        h4 = self.addHost('h4', mac = '00:00:00:00:00:04')
        h5 = self.addHost('h5', mac = '00:00:00:00:00:05')
        h6 = self.addHost('h6', mac = '00:00:00:00:00:06')
        # Links
        # Switch 1
        self.addLink(h1, s1, 1, 2)
        self.addLink(h2, s1, 3, 4)
        self.addLink(s1, s2, 5, 6)
        # Switch 2
        self.addLink(h3, s2, 7, 8)
        self.addLink(h4, s2, 9, 10)
        self.addLink(s2, s3, 11, 12)
        # Switch 3
        self.addLink(h5, s3, 13, 14)
        self.addLink(h6, s3, 15, 16)
        self.addLink(s3, s4, 17, 18)
        #Switch 4
        self.addLink(s4, s1, 19, 20)

topos = {'MyTopo': (lambda: TwoWayTopology())}
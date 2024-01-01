#!/usr/bin/python

from mininet.topo import Topo
from mininet.net import Mininet
from mininet.util import dumpNodeConnections
from mininet.cli import CLI


class part1_topo(Topo):
    def build(self):
        # switch1 = self.addSwitch('switchname')
        # host1 = self.addHost('hostname')
        # self.addLink(hostname,switchname)
        switch1 = self.addSwitch('switch1')
        host1   = self.addHost('host1')
        host2   = self.addHost('host2')
        host3   = self.addHost('host3')
        host4   = self.addHost('host4')
        self.addLink(host1,switch1)
        self.addLink(host2,switch1)
        self.addLink(host3,switch1)
        self.addLink(host4,switch1)


topos = {"part1": part1_topo}

if __name__ == "__main__":
    t = part1_topo()
    net = Mininet(topo=t, controller=None)
    net.start()
    CLI(net)
    net.stop()

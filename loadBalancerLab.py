#!/usr/bin/python

from mininet.topo import Topo
from mininet.net import Mininet
from mininet.node import Node,Host
from mininet.nodelib import LinuxBridge
from mininet.log import setLogLevel, info
from mininet.cli import CLI
from consoles import *




class LinuxRouter( Node ):
    "A Node with IP forwarding enabled."

    def config( self, **params ):
        super( LinuxRouter, self).config( **params )
        # Enable forwarding on the router
        self.cmd( 'sysctl net.ipv4.ip_forward=1' )

    def terminate( self ):
        self.cmd( 'sysctl net.ipv4.ip_forward=0' )
        super( LinuxRouter, self ).terminate()




class LB ( Node ):
    pass
class Client ( Host ):
    pass
class Server ( Host ):
    pass
        
class LbTopo( Topo ):

    def build( self, **_opts ):

        defaultIP = '10.0.0.1/8'  # IP address for r0-eth1
        lb1 = self.addNode( 'lb1', cls=LB , ip=defaultIP )

        s1, s2 = [ self.addSwitch( s ) for s in 's1', 's2' ]

        self.addLink( s1, lb1, intfName2='lb1-eth1',
                      params2={ 'ip' : defaultIP } )  # for clarity
        self.addLink( s2, lb1, intfName2='lb1-eth2',
                      params2={ 'ip' : '192.168.0.1/24' } )

        h1 = self.addHost( 'h1', cls=Client, ip='10.0.0.101/8',
                           defaultRoute='via 10.0.0.1' )
        h2 = self.addHost( 'h2', cls=Client, ip='10.0.0.102/8',
                           defaultRoute='via 172.16.0.1' )
        h3 = self.addHost( 'h3', cls=Client,ip='10.0.0.103/8',
                           defaultRoute='via 10.0.0.1' )
        h4 = self.addHost( 'h4', cls=Client, ip='10.0.0.104/8',
                           defaultRoute='via 10.0.0.1' )
        h5 = self.addHost( 'h5', cls=Client, ip='10.0.0.105/8',
                           defaultRoute='via 10.0.0.1' )

        serv1 = self.addHost( 'serv1', cls=Server, ip='192.168.0.101/24',
                              defaultRoute='via 192.168.0.1' )
        serv2 = self.addHost( 'serv2', cls=Server, ip='192.168.0.102/24',
                              defaultRoute='via 192.168.0.1' )
        serv3 = self.addHost( 'serv3', cls=Server, ip='192.168.0.103/24',
                              defaultRoute='via 192.168.0.1' )

        for h, s in [ (h1, s1), (h2, s1), (h3, s1), (h4,s1), (h5,s1), (s2,serv1), (s2,serv2), (s2,serv3) ]:
            self.addLink( h, s )


def run():

    topo = LbTopo()
    net = Mininet( topo=topo, switch=LinuxBridge, controller = None )  # controller is used by s1-s3
    net.start()

    app = ConsoleApp ( net, width = 3 )
    app.mainloop()

    # for serv in ['serv1','serv2']:
    #     serverNode = net.get(serv)
    #     serverNode.cmd( 'xterm -e sudo python server.py VIDEO > %s.log 2>&1 &' % serv )

    # serverNode = net.get('serv3')
    # serverNode.cmd( 'xterm -e sudo python server.py MUSIC > serv3.log 2>&1 &' )

    # LBNode = net.get('lb1')
    # LBNode.cmd('xterm -e sudo python lb.py > lb.log 2>&1 &')


    # CLI( net )

    net.stop()

if __name__ == '__main__':
    setLogLevel( 'info' )
    run()

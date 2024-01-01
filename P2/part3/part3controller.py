# Part 3 of UWCSE's Mininet-SDN project
#
# based on Lab Final from UCSC's Networking Class
# which is based on of_tutorial by James McCauley

from pox.core import core
import pox.openflow.libopenflow_01 as of
from pox.lib.addresses import IPAddr, IPAddr6, EthAddr

log = core.getLogger()

# Convenience mappings of hostnames to ips
IPS = {
    "h10": "10.0.1.10",
    "h20": "10.0.2.20",
    "h30": "10.0.3.30",
    "serv1": "10.0.4.10",
    "hnotrust": "172.16.10.100",
}

# Convenience mappings of hostnames to subnets
SUBNETS = {
    "h10": "10.0.1.0/24",
    "h20": "10.0.2.0/24",
    "h30": "10.0.3.0/24",
    "serv1": "10.0.4.0/24",
    "hnotrust": "172.16.10.0/24",
}


class Part3Controller(object):
    """
    A Connection object for that switch is passed to the __init__ function.
    """

    def __init__(self, connection):
        print(connection.dpid)
        # Keep track of the connection to the switch so that we can
        # send it messages!
        self.connection = connection

        # This binds our PacketIn event listener
        connection.addListeners(self)
        # use the dpid to figure out what switch is being created
        if connection.dpid == 1:
            self.s1_setup()
        elif connection.dpid == 2:
            self.s2_setup()
        elif connection.dpid == 3:
            self.s3_setup()
        elif connection.dpid == 21:
            self.cores21_setup()
        elif connection.dpid == 31:
            self.dcs31_setup()
        else:
            print("UNKNOWN SWITCH")
            exit(1)

    def flood_connection(self):
      msg = of.ofp_flow_mod()
      action = of.ofp_action_output(port = of.OFPP_FLOOD)
      msg.actions.append(action)
      self.connection.send(msg)

    def s1_setup(self):
        #put switch 1 rules here
        self.flood_connection()
    def s2_setup(self):
        #put switch 2 rules here
        self.flood_connection()

    def s3_setup(self):
        #put switch 3 rules here
        self.flood_connection()

    def cores21_setup(self):
        # Delete all connections
        # Why does increasing prio brick my code huh???
        block1 = of.ofp_flow_mod()
        block1.match.nw_proto = 1
        block1.match.dl_type = 0x0800
        block1.match.nw_src = IPS["hnotrust"]
        self.connection.send(block1)

        block2 = of.ofp_flow_mod()
        block2.match.dl_type = 0x0800
        block2.match.nw_src = IPS["hnotrust"]
        block2.match.nw_dst = IPS["serv1"]
        self.connection.send(block2)

        # Allow for perms of other things
        # host 10
        h1 = of.ofp_flow_mod()
        h1.match.dl_type = 0x0800
        h1.match.nw_dst = IPS["h10"]
        action1 = of.ofp_action_output(port = 1)
        h1.actions.append(action1)
        self.connection.send(h1)
        
        # host 20
        h2 = of.ofp_flow_mod()
        h2.match.dl_type = 0x0800
        h2.match.nw_dst = IPS["h20"]
        action2 = of.ofp_action_output(port = 2)
        h2.actions.append(action2)
        self.connection.send(h2)
        
        # host 30
        h3 = of.ofp_flow_mod()
        h3.match.dl_type = 0x0800
        h3.match.nw_dst = IPS["h30"]
        action3 = of.ofp_action_output(port = 3)
        h3.actions.append(action3)
        self.connection.send(h3)

        # I'm just confused tbh why adding this rule sometimes screws things
        # server
        hserv = of.ofp_flow_mod()
        hserv.match.dl_type = 0x0800
        hserv.match.nw_dst = IPS["serv1"]
        actionserv = of.ofp_action_output(port = 4)
        hserv.actions.append(actionserv)
        self.connection.send(hserv)

        self.flood_connection()

    def dcs31_setup(self):
        #put datacenter switch rules here
        self.flood_connection()

    # used in part 4 to handle individual ARP packets
    # not needed for part 3 (USE RULES!)
    # causes the switch to output packet_in on out_port
    def resend_packet(self, packet_in, out_port):
        msg = of.ofp_packet_out()
        msg.data = packet_in
        action = of.ofp_action_output(port=out_port)
        msg.actions.append(action)
        self.connection.send(msg)

    def _handle_PacketIn(self, event):
        """
        Packets not handled by the router rules will be
        forwarded to this method to be handled by the controller
        """

        packet = event.parsed  # This is the parsed packet data.
        if not packet.parsed:
            log.warning("Ignoring incomplete packet")
            return

        packet_in = event.ofp  # The actual ofp_packet_in message.
        print(
            "Unhandled packet from " + str(self.connection.dpid) + ":" + packet.dump()
        )


def launch():
    """
    Starts the component
    """

    def start_switch(event):
        log.debug("Controlling %s" % (event.connection,))
        Part3Controller(event.connection)

    core.openflow.addListenerByName("ConnectionUp", start_switch)

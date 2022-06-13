from pox.core import core
import pox.openflow.libopenflow_01 as of
from pox.lib.util import dpid_to_str, str_to_dpid
from pox.lib.util import str_to_bool
import time

log = core.getLogger()

_flood_delay = 0

class Controller(object):
    def __init__(self, connection):
        self.connection = connection
        connection.addListeners(self)

        # Forward table
        self.macToPort = {}

        if connection.dpid == 1:
            self.s1_setup()
        elif connection.dpid == 2:
            self.s2_setup()
        elif connection.dpid == 3:
            self.s3_setup()
        elif connection.dpid == 4:
            self.s4_setup()

    """
    This setup rules will define to which port can each switch output
    a packet with unknown destination.
    """
    def s1_setup(self):
        # Switch 1 rules
        self.allowed_ports = [2, 4, 5]
    
    def s2_setup(self):
        # Switch 2 rules
        self.allowed_ports = [8, 10, 11]

    def s3_setup(self):
        # Switch 3 rules
        self.allowed_ports = [14, 16, 17]

    def s4_setup(self):
        # Switch 4 rules
        self.allowed_ports = [19]
    
    def resend_packet (self, packet_in, out_port):
        """
        Instructs the switch to resend a packet that it had sent to us.
        "packet_in" is the ofp_packet_in object the switch had sent to the
        controller due to a table-miss.
        """
        msg = of.ofp_packet_out()
        msg.data = packet_in

        # Add an action to send to the specified port
        for i in out_port:
            action = of.ofp_action_output(port = i)
            msg.actions.append(action)

        # Send message to switch
        self.connection.send(msg)

    def act_like_switch(self, packet, packet_in):
        """
        Implement switch-like behavior.
        """
        if self.connection.dpid == 3:
            log.info(f"INCOMING PACKET FROM {packet.src} TO {packet.dst} PORT {packet_in.in_port}")
        if packet_in.in_port not in self.allowed_ports:
            return

        self.macToPort[packet.src] = packet_in.in_port

        # Learn the port for the source MAC
        if packet.dst in self.macToPort:
            self.macToPort[packet.src] = packet_in.in_port

            #if the port associated with the destination MAC of the packet is known:
            # Send packet out the associated port
            #self.resend_packet(packet_in, ...)

            # Once you have the above working, try pushing a flow entry
            # instead of resending the packet (comment out the above and
            # uncomment and complete the below.)

            log.debug("Installing flow...")
            # Maybe the log statement should have source/destination/port?

            msg = of.ofp_flow_mod()
            #
            ## Set fields to match received packet
            msg.match = of.ofp_match.from_packet(packet, packet_in.in_port)
            msg.idle_timeout = 10
            msg.hard_timeout = 30
            msg.actions.append(of.ofp_action_output(port = self.macToPort[packet.dst]))
            msg.data = packet_in # 6a
            self.connection.send(msg)
            #
            #< Set other fields of flow_mod (timeouts? buffer_id?) >
            #
            #< Add an output action, and send -- similar to resend_packet() >
        else:
            # Flood the packet out everything but the input port
            self.resend_packet(packet_in, self.allowed_ports)
        
    def _handle_PacketIn (self, event):
        """
        Handles packet in messages from the switch.
        """

        packet = event.parsed # This is the parsed packet data.
        if not packet.parsed:
            log.warning("Ignoring incomplete packet")
            return

        packet_in = event.ofp # The actual ofp_packet_in message.

        # Comment out the following line and uncomment the one after
        # when starting the exercise.
        #self.act_like_hub(packet, packet_in)
        self.act_like_switch(packet, packet_in)

def launch ():
  """
  Starts the component
  """
  def start_switch (event):
    log.debug("Controlling %s" % (event.connection,))
    Controller(event.connection)
  core.openflow.addListenerByName("ConnectionUp", start_switch)
from pox.core import core
import pox.openflow.libopenflow_01 as of
from pox.lib.util import dpid_to_str, str_to_dpid
from pox.lib.util import str_to_bool
from pox.lib.addresses import EthAddr
import time

log = core.getLogger()

_flood_delay = 0

class Controller(object):
    def __init__(self, connection, transparent):
        self.connection = connection
        connection.addListeners(self)

        self.transparent = transparent

        self.hold_down_expired = _flood_delay == 0

        # Routing table
        self.macToPort = {}
        # Switch blacklist
        self.black_list = {}

        if connection.dpid == 1:
            self.s1_setup()
        elif connection.dpid == 2:
            self.s2_setup()
        elif connection.dpid == 3:
            self.s3_setup()
        elif connection.dpid == 4:
            self.s4_setup()
        else:
            self.s5_setup()

    """
    This setup rules will define to which port can each switch output
    a packet with unknown destination.
    """
    def s1_setup(self):
        # Switch 1 rules
        self.allowed_ports = {2, 4, 5}
        self.black_list[EthAddr('00:00:00:00:00:01')] = [
            EthAddr('00:00:00:00:00:02'), EthAddr('00:00:00:00:00:03'),
             EthAddr('00:00:00:00:00:04'), EthAddr('00:00:00:00:00:05'), 
             EthAddr('00:00:00:00:00:06'), EthAddr('00:00:00:00:00:08')
        ]
        self.black_list[EthAddr('00:00:00:00:00:02')] = [
            EthAddr('00:00:00:00:00:01'), EthAddr('00:00:00:00:00:03'),
             EthAddr('00:00:00:00:00:04'), EthAddr('00:00:00:00:00:05'), 
             EthAddr('00:00:00:00:00:06'), EthAddr('00:00:00:00:00:08')
        ]
    
    def s2_setup(self):
        # Switch 2 rules
        self.allowed_ports = {8, 10, 11}
        self.black_list[EthAddr('00:00:00:00:00:03')] = [
            EthAddr('00:00:00:00:00:01'), EthAddr('00:00:00:00:00:02'),
             EthAddr('00:00:00:00:00:04'), EthAddr('00:00:00:00:00:05'), 
             EthAddr('00:00:00:00:00:06'), EthAddr('00:00:00:00:00:07')
        ]
        self.black_list[EthAddr('00:00:00:00:00:04')] = [
            EthAddr('00:00:00:00:00:01'), EthAddr('00:00:00:00:00:02'),
             EthAddr('00:00:00:00:00:03'), EthAddr('00:00:00:00:00:05'), 
             EthAddr('00:00:00:00:00:06'), EthAddr('00:00:00:00:00:07')
        ]

    def s3_setup(self):
        # Switch 3 rules
        self.allowed_ports = {14, 16, 17}
        self.black_list[EthAddr('00:00:00:00:00:05')] = [
            EthAddr('00:00:00:00:00:01'), EthAddr('00:00:00:00:00:02'),
             EthAddr('00:00:00:00:00:03'), EthAddr('00:00:00:00:00:04'), 
             EthAddr('00:00:00:00:00:06'), EthAddr('00:00:00:00:00:07')
        ]
        self.black_list[EthAddr('00:00:00:00:00:06')] = [
            EthAddr('00:00:00:00:00:01'), EthAddr('00:00:00:00:00:02'),
             EthAddr('00:00:00:00:00:03'), EthAddr('00:00:00:00:00:04'), 
             EthAddr('00:00:00:00:00:05'), EthAddr('00:00:00:00:00:07')
        ]

    def s4_setup(self):
        # Switch 4 rules
        self.allowed_ports = {19, 21}

    def s5_setup(self):
        # Switch 5 rules
        self.allowed_ports = {24, 26, 27}

        # Blacklisted address
        self.black_list[EthAddr('00:00:00:00:00:07')] = [
            EthAddr('00:00:00:00:00:03'), EthAddr('00:00:00:00:00:04'),
             EthAddr('00:00:00:00:00:05'), EthAddr('00:00:00:00:00:06'),
             EthAddr('00:00:00:00:00:08')
        ]
        self.black_list[EthAddr('00:00:00:00:00:08')] = [
            EthAddr('00:00:00:00:00:01'), EthAddr('00:00:00:00:00:02'),
            EthAddr('00:00:00:00:00:07')
        ]
    
    def _handle_PortStatus (self, event):
        if not event.added:
            for key in self.macToPort:
                if self.macToPort[key] == event.port:
                    del self.macToPort[key]
                    return
        
    def _handle_PacketIn (self, event):
        """
        Handles packet in messages from the switch.
        """

        packet = event.parsed

        def flood(message = None):
            """ Floods the packet (Sends the packets to all ports) """

            msg = of.ofp_packet_out()
            if time.time() - self.connection.connect_time >= _flood_delay:
                # Only flood if we've been connected for a little while...

                if self.hold_down_expired is False:
                    # Oh yes it is!
                    self.hold_down_expired = True
                    log.info("%s: Flood hold-down expired -- flooding",
                        dpid_to_str(event.dpid))

                if message is not None:
                     log.debug(message)
                
                # Here we implement the unidirectional link logic.
                # We will flood the packet only on allowed direction given
                # by the allowed outpot ports.
                for port in self.allowed_ports:
                    if port != event.port:
                        msg.actions.append(of.ofp_action_output(port = port))
            else:
                pass
                #log.info("Holding down flood for %s", dpid_to_str(event.dpid))
            msg.data = event.ofp
            msg.in_port = event.port
            self.connection.send(msg)

            packet = event.parsed # This is the parsed packet data.
            if not packet.parsed:
                log.warning("Ignoring incomplete packet")
            return
    
        def drop(duration=None):
            """
            Drops this packet and optionally installs a flow to continue
            dropping similar ones for a while
            """

            if duration is not None:
                if not isinstance(duration, tuple):
                    duration = (duration,duration)
                msg = of.ofp_flow_mod()
                msg.match = of.ofp_match.from_packet(packet)
                msg.idle_timeout = duration[0]
                msg.hard_timeout = duration[1]
                msg.buffer_id = event.ofp.buffer_id
                self.connection.send(msg)
            elif event.ofp.buffer_id is not None:
                msg = of.ofp_packet_out()
                msg.buffer_id = event.ofp.buffer_id
                msg.in_port = event.port
                self.connection.send(msg)

        # If the port is in the list of allowed ports then we know
        # that if another packet arrives with destination packet.src
        # then the switch should forward it to the event.port.
        if event.port in self.allowed_ports:
            self.macToPort[packet.src] = event.port

        # If the port associated with packet.src is known and the packet
        # is arriving from a different port then we have a loop and we
        # we should drop the packet.
        if packet.src in self.macToPort:
            port = self.macToPort[packet.src]
            if port != event.port:
                drop(10)
                return
        
        # Check if packet src is in blacklist. This will prevent host to
        # host communication.
        if packet.dst in self.black_list:
            if packet.src in self.black_list[packet.dst]:
                # Address is blacklisted, drop packet.
                drop()
                return

        if packet.dst.is_multicast:
            flood() # 3a
        else:
            if packet.dst not in self.macToPort: # 4
                flood("Port for %s unknown -- flooding" % (packet.dst,)) # 4a
            else:
                port = self.macToPort[packet.dst]
                if port == event.port: # 5
                    # 5a
                    log.warning("Same port for packet from %s -> %s on %s.%s.  Drop."
                        % (packet.src, packet.dst, dpid_to_str(event.dpid), port))
                    drop(10)
                    return
                # 6
                log.debug("installing flow for %s.%i -> %s.%i" %
                        (packet.src, event.port, packet.dst, port))

                log.debug(f"S{self.connection.dpid}: Incoming packet on port from {packet.src} to {packet.dst}")

                msg = of.ofp_flow_mod()
                msg.match = of.ofp_match.from_packet(packet, event.port)
                msg.idle_timeout = 10
                msg.hard_timeout = 30
                msg.actions.append(of.ofp_action_output(port = port))
                msg.data = event.ofp # 6a
                self.connection.send(msg)

class l2_learning (object):
  """
  Waits for OpenFlow switches to connect and makes them learning switches.
  """
  def __init__ (self, transparent, ignore = None):
    """
    Initialize

    See LearningSwitch for meaning of 'transparent'
    'ignore' is an optional list/set of DPIDs to ignore
    """
    core.openflow.addListeners(self)
    self.transparent = transparent
    self.ignore = set(ignore) if ignore else ()

  def _handle_ConnectionUp (self, event):
    if event.dpid in self.ignore:
      log.debug("Ignoring connection %s" % (event.connection,))
      return
    log.debug("Connection %s" % (event.connection,))
    Controller(event.connection, self.transparent)


def launch (transparent=False, hold_down=_flood_delay, ignore = None):
  """
  Starts an L2 learning switch.
  """
  try:
    global _flood_delay
    _flood_delay = int(str(hold_down), 10)
    assert _flood_delay >= 0
  except:
    raise RuntimeError("Expected hold-down to be a number")

  if ignore:
    ignore = ignore.replace(',', ' ').split()
    ignore = set(str_to_dpid(dpid) for dpid in ignore)

  core.registerNew(l2_learning, str_to_bool(transparent), ignore)
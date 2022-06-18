"""
This firewall works in the following way:

  - All non TCP packets will be blocked with
   the exception of ARP packets, this will be used
   for MAC discovery on the link layer.

  - Since the HTTP servers will run on port 80, all
    packets coming from client hosts whose TCP 
    destination port is not 80 will be blocked.
  
  - On the client side the hosts will open a random
    TCP port to send HTTP messages to the server so
    we should not block packets whose source address
    is a HTTP server and have a TCP destination port
    different from 80. 
"""

from pox.core import core
from pox.lib.addresses import *
import pox.lib.packet as pkt

# A set of ports to keep unblocked.
unblocked_ports = set()

# A set of server addresses to keep unblocked.
unblocked_addreses = {EthAddr('00:00:00:00:00:07'), EthAddr('00:00:00:00:00:08')}

def block_handler (event):
  # Handles packet events and kills the ones with a blocked port number.
  
  packet = event.parsed
  tcpp = packet.find('tcp')
  if not tcpp:
    
      # Not TCP, check if ARP otherwise block.
      if packet.find('arp'):
          return
      core.getLogger("blocker").debug(f"BLOQUEADO {packet.src}")    
      event.halt = True
  if tcpp is None:
      return
  if tcpp.dstport not in unblocked_ports and packet.src not in unblocked_addreses:
      # Halt the event, stopping l2_learning from seeing it
      # (and installing a table entry for it)
      core.getLogger("blocker").debug(f"BLOQUEADO {tcpp.dstport}")
      event.halt = True

def block (*ports):
  unblocked_ports.difference_update(ports)

def unblock (*ports):
  unblocked_ports.update(ports)

def launch (ports = ''):

  # Add ports from commandline to list of ports to block
  unblocked_ports.update(int(x) for x in ports.replace(",", " ").split())

  # Add functions to Interactive so when you run POX with py, you
  # can easily add/remove ports to block.
  core.Interactive.variables['block'] = block
  core.Interactive.variables['unblock'] = unblock

  # Listen to packet events
  core.openflow.addListenerByName("PacketIn", block_handler)
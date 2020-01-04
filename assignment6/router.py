# Router
# Auther: Yuanjie Yue
# Date: 12/05/19

import os.path
import socket
import table
import threading
import util
import struct
import sys

_CONFIG_UPDATE_INTERVAL_SEC = 5

_MAX_UPDATE_MSG_SIZE = 1024
_BASE_ID = 8000

_INF = sys.maxsize

def _ToPort(router_id):
  return _BASE_ID + router_id

def _ToRouterId(port):
  return port - _BASE_ID

class Router:
  def __init__(self, config_filename):
    # ForwardingTable has 3 columns (DestinationId,NextHop,Cost). It's
    # threadsafe.
    self._forwarding_table = table.ForwardingTable()
    # Config file has router_id, neighbors, and link cost to reach
    # them.
    self._config_filename = config_filename
    self._router_id = None
    # Socket used to send/recv update messages (using UDP).
    self._socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    # Dict holds the cost of current router to the neighbors 
    self._cost_to_neighbors = {}
    # Dict holds the neighbors dest cost infos
    self._neighbors_dest_infos = {}

  def start(self):
    # Start a periodic closure to update config.
    self._config_updater = util.PeriodicClosure(
        self.load_config, _CONFIG_UPDATE_INTERVAL_SEC)
    self._config_updater.start()
    # TODO: init and start other threads.
    while True: 
      msg, addr = self._socket.recvfrom(1024)
      #get sender router id
      current_neighbor_id = _ToRouterId(addr[1])
      #get forwarding table
      forwarding_table = self._forwarding_table.get_table()
      current_neighbor_dest_infos = self.parse_update_msg(msg)

      update = False
      # bellman ford logic goes here
      for neighbor_dest_id, neighbor_dest_cost in current_neighbor_dest_infos.items():
        # init the current neighor if it is not exist
        if not current_neighbor_id in self._neighbors_dest_infos:
            self._neighbors_dest_infos[current_neighbor_id] = {}
        self._neighbors_dest_infos[current_neighbor_id][neighbor_dest_id] = neighbor_dest_cost
        if neighbor_dest_id != self._router_id:
          # init the pre cost and origin cost to infinite
          pre_cost, origin_cost = _INF, _INF
          if neighbor_dest_id in forwarding_table:
            origin_cost = forwarding_table[neighbor_dest_id][1]
          else:
            update = True
          # keep relaxing each edge if there is a short path.
          for neighbor_id, cost in self._cost_to_neighbors.items():
            if neighbor_id in self._neighbors_dest_infos and neighbor_dest_id in self._neighbors_dest_infos[neighbor_id]:
              new_cost = self._cost_to_neighbors[neighbor_id] + self._neighbors_dest_infos[neighbor_id][neighbor_dest_id]
              # if shorter path, then relax the current edge
              if new_cost < pre_cost:
                pre_cost = new_cost
                forwarding_table[neighbor_dest_id] = (neighbor_id, new_cost)
          if neighbor_dest_id in forwarding_table and origin_cost != forwarding_table[neighbor_dest_id][1]:
            update = True
      if update:
        update_msg = self.generate_update_msg(self._forwarding_table.snapshot())
        print(self._forwarding_table)
        self.broadcast(update_msg)

  def stop(self):
    if self._config_updater:
      self._config_updater.stop()
    # TODO: clean up other threads.

  def load_config(self):
    assert os.path.isfile(self._config_filename)
    with open(self._config_filename, 'r') as f:
      router_id = int(f.readline().strip())
      # Only set router_id when first initialize.
      # here we could change the value of cost in the config file while running
      # PeriodicClosure could help load the config every 5 secs.
      if not self._router_id:
        self._socket.bind(('localhost', _ToPort(router_id)))
        self._router_id = router_id
        # initialize the forwarding table 
        new_snapshot = []
        new_snapshot.append((router_id, router_id, 0))

        self._forwarding_table.reset(new_snapshot)
        print(self._forwarding_table)

      # now read the neighbor cost infos
      lines = self.read_lines(f)
      neighbor_costs = map(lambda x: x.split(','), lines)
      for (router_id, cost) in neighbor_costs:
        self._cost_to_neighbors[int(router_id)] = int(cost)
      update_msg = self.generate_update_msg(self._forwarding_table.snapshot())
      # broadcasting the change to the neighbors
      self.broadcast(update_msg)

  # broadcast the msg to all the neighbors.
  def broadcast(self, msg):
    for (neighbor_id, cost) in self._cost_to_neighbors.items():
      self._socket.sendto(msg, ('localhost', _ToPort(neighbor_id)))
  
  # parse the givne msg
  def parse_update_msg(self, msg):
    offset = 0
    size = struct.unpack_from('!h', msg, offset)[0]
    res = {}
    for i in range(size):
      offset += 2
      router_id = struct.unpack_from('!h', msg, offset)[0]
      offset += 2
      cost = struct.unpack_from('!h', msg, offset)[0]
      res[router_id] = cost
    return res

  # generate an update msg
  def generate_update_msg(self, snapshot):
    msg = bytearray()
    size = len(snapshot)
    msg += struct.pack('!h', size)
    for (router_id, next_hop, cost) in snapshot:
      msg += struct.pack('!h', int(router_id))
      msg += struct.pack('!h', int(cost))
    return bytes(msg)

  # read lines from the given file
  def read_lines(self, file):
    lines = []
    end = False
    while not end:
      line = file.readline().strip()
      if line:
        lines.append(line)
      else:
        end = True
    return lines

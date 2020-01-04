import os.path
import socket
import table
import threading
import util
import sys
import struct

_CONFIG_UPDATE_INTERVAL_SEC = 5

_MAX_UPDATE_MSG_SIZE = 1024
_BASE_ID = 8000

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
        self.neighbors = []
        self.neighborsAndCost = {}
        self.neighborsTable = {}


    def start(self):
        # Start a periodic closure to update config.
        self._config_updater = util.PeriodicClosure(
            self.load_config, _CONFIG_UPDATE_INTERVAL_SEC)
        self._config_updater.start()
        self.load_config()
        # TODO: init and start other threads.
        while True:
          if self.recMsgAndUpdateTable():
            self.sendMessage()


    def stop(self):
        if self._config_updater:
          self._config_updater.stop()
        # TODO: clean up other threads.

    def load_config(self):
        assert os.path.isfile(self._config_filename)
        with open(self._config_filename, 'r') as f:
          router_id = int(f.readline().strip())
          # Only set router_id when first initialize.
          snapshot = []
          if not self._router_id:
            self._socket.bind(('localhost', _ToPort(router_id)))
            self._router_id = router_id
            # initialize the forwarding table
            for x in f:
              strlist = x.strip().split(",")
              neighbor = int(strlist[0])
              cost = int(strlist[1])
              self.neighbors.append(neighbor)
              self.neighborsAndCost[neighbor] = cost

            snapshot.append((router_id,router_id,0))
            self._forwarding_table.reset(snapshot)
          else:
            for x in f:
              strlist = x.strip().split(",")
              neighbor = int(strlist[0])
              cost = int(strlist[1])
              self.neighborsAndCost[neighbor] = cost
          self.sendMessage()

    def setNeighborInfo(self, router_id, des_router, cost_to_des):
        if not router_id in self.neighborsTable:
            self.neighborsTable[router_id] = {}
        self.neighborsTable[router_id][des_router] = cost_to_des


    def recMsgAndUpdateTable(self):
        message, addr = self._socket.recvfrom(1024)
        #get sender router id
        router_id = _ToRouterId(addr[1])
        #get forwarding table
        get_table = self._forwarding_table.getTable()
        #number of des cost neighbor to me
        entry_count = struct.unpack('!h',message[0:2])[0]

        ifUpdate = False
        for i in range(2, 2 + 4 * entry_count, 4):
          des_router = struct.unpack('!h', message[i:i+2])[0]
          cost_to_des = struct.unpack('!h', message[i+2:i+4])[0]
          self.setNeighborInfo(router_id, des_router, cost_to_des)
          precost = sys.maxsize
          origincost = sys.maxsize
          if des_router in get_table:
            origincost = get_table[des_router][1]

          if des_router == self._router_id:
            continue

          if not des_router in get_table:
            ifUpdate = True

          for neighbor in self.neighbors:
            if neighbor in self.neighborsTable:
              if des_router in self.neighborsTable[neighbor]:
                newCost = self.neighborsAndCost[neighbor]+self.neighborsTable[neighbor][des_router]
                if newCost < precost:
                  precost = newCost
                  get_table[des_router] = (neighbor, newCost)
          if (des_router in get_table) and (not origincost == get_table[des_router][1]):
            ifUpdate = True
        return ifUpdate


    def sendMessage(self):
        msg = b''
        entry_count = self._forwarding_table.size()
        msg += struct.pack('!h', entry_count)
        snapshot = self._forwarding_table.snapshot()
        for (dest, next_hop, cost) in snapshot:
          msg += struct.pack('!h', int(dest))
          msg += struct.pack('!h', int(cost))
        for i in self.neighbors:
          self._socket.sendto(msg, ('localhost', _ToPort(i)))
        print(self._forwarding_table.__str__())

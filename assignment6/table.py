import os
import threading


# Class that abstract routing table. This class is thread safe.
class ForwardingTable:
  # Constructor. '_table' is dictionary keyed on router ID, and values
  # are (next_hop,cost) pairs.
  def __init__(self):
    self._table = {}
    self._lock = threading.Lock()

  def get_table(self):
    return self._table

  # Return current forwarding table as a list of tuples
  # (id,next_hop,cost).
  def snapshot(self):
    entries = []
    with self._lock:
      for router_id in self._table:
        next_hop, cost = self._table[router_id]
        entries.append((router_id, next_hop, cost))
    return entries


  # Reset routing table by snapshot, where snapshot is a list of
  # tuples (id,next_hop,cost).
  def reset(self, snapshot):
    with self._lock:
      self._table = {}
      for (dest, next_hop, cost) in snapshot:
        self._table[dest] = (next_hop, cost)


  # Return current number of entries in forwarding table.
  def size(self):
    return len(self._table)


  def __str__(self):
    entries = ['ID\tNextHop\tCost' + os.linesep]
    with self._lock:
      for router_id in self._table:
        next_hop, cost = self._table[router_id]
        entries.append(''.join([str(router_id), '\t',
                                str(next_hop), '\t',
                                str(cost), os.linesep]))
    return ''.join(entries)

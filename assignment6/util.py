import threading


# Convenient class to run a function periodically in a separate
# thread.
class PeriodicClosure:
  def __init__(self, handler, interval_sec):
    self._handler = handler
    self._interval_sec = interval_sec
    self._timer = None

  def _timeout_handler(self):
    self._handler()
    self.start()

  def start(self):
    self._timer = threading.Timer(self._interval_sec, self._timeout_handler)
    self._timer.start()

  def stop(self):
    if self._timer:
      self._timer.cancel()

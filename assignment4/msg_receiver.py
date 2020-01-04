import config
import sys
import time
import util


def msg_handler(msg):
  print(repr(msg))


if __name__ == '__main__':
  if len(sys.argv) != 2:
    print('Usage: python msg_receiver.py [dummy|sw|gbn]')
    sys.exit(1)

  transport_layer = None
  name = sys.argv[1]
  try:
    transport_layer = util.get_transport_layer_by_name(
        name, config.RECEIVER_LISTEN_PORT,
        config.SENDER_LISTEN_PORT, msg_handler)
    while True:
      time.sleep(1)
  finally:
    if transport_layer:
      transport_layer.shutdown()

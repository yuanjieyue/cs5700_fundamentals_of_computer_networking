import config
import sys
import util


if __name__ == '__main__':
  if len(sys.argv) != 2:
    print('Usage: python msg_sender.py [dummy|sw|gbn]')
    sys.exit(1)

  transport_layer = None
  name = sys.argv[1]
  try:
    transport_layer = util.get_transport_layer_by_name(
        name, config.SENDER_LISTEN_PORT,
        config.RECEIVER_LISTEN_PORT, None)
    for i in range(20):
      msg = 'MSG:' + str(i)
      print(msg.encode())
      while not transport_layer.send(msg.encode()):
        pass
  finally:
    if transport_layer:
      transport_layer.shutdown()

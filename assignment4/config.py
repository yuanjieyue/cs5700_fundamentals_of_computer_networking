# Port numbers used by unreliable network layers.
SENDER_LISTEN_PORT = 8080
RECEIVER_LISTEN_PORT = 8081

# Parameters for unreliable network.
BIT_ERROR_PROB = 0.1
MSG_LOST_PROB = 0.1

# Parameters for transport protocols.
TIMEOUT_MSEC = 3
WINDOW_SIZE = 20

# Packet size for network layer.
MAX_SEGMENT_SIZE = 512
# Packet size for transport layer.
MAX_MESSAGE_SIZE = 500

# Message types used in transport layer.
MSG_TYPE_DATA = 1
MSG_TYPE_ACK = 2

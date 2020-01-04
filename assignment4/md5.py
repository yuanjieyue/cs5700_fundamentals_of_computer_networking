import hashlib
import sys


if __name__ == "__main__":
  if len(sys.argv) != 2:
    print('Usage: python md5 file_name')
    sys.exit(1)

  md5 = hashlib.md5()
  with open(sys.argv[1], 'rb') as f:
    while True:
      block = f.read(1024)
      if not block: break
      md5.update(block)
  digest = md5.digest()
  print('digest:', digest)
  # print('digest length:', len(digest))
  print('digest as hex:', digest.hex())
  # print('digest length:', len(digest.hex()))

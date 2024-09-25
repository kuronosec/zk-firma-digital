import struct

# Some utility libraries to process the input data as the
# Circom circuit requires
def splitToWords(number, wordsize, number_element):
  t = number
  words = []
  base_two = 2

  for i in range(number_element):
    words.append(str(t % pow(base_two, wordsize)))
    t = t // pow(base_two, wordsize)

  if (t != 0):
    raise ValueError(f"Number {number} does not fit in {wordsize * number_element} bits")

  return words

def preprocess_message_for_sha256(message: bytearray, max_len: int) -> bytearray:
    # Step 1: Calculate the original message length in bits
    original_bit_len = len(message) * 8

    # Step 2: Add the '1' bit, represented as 0x80 in hexadecimal (10000000 in binary)
    message.append(0x80)

    # Step 3: Add padding of zeros (bytes of 0x00) until message length is congruent to 448 mod 512
    # 448 mod 512 because we need 64 bits for the length at the end (512 - 64 = 448)
    while (len(message) * 8) % 512 != 448:
        message.append(0x00)

    # Step 4: Append the original length of the message as a 64-bit big-endian integer
    message += struct.pack('>Q', original_bit_len)

    # Step 5: If the final message length exceeds max_len, pad it with zeroes to max_len
    message_len = len(message)
    if message_len > max_len:
        print(message_len)
        raise ValueError("Message length exceeds the maximum length")
    elif message_len < max_len:
        message += bytearray(max_len - len(message))

    return message, message_len
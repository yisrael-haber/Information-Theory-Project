"""
Done by: Yisrael Haber, Hadar Kaner

In this script we concatenate the Lempel-Ziv and Huffman algorithms in order to compress a file. In order to compress a file enter 
and then we decompress it to get the original file.
The only requirement for the script is to have the dickens.txt file in the same directory as this script.
The original file is 31.46 MB, and the compressed file is only 11.61 MB.
Total Run Time - about 3 minutes.
"""
from tqdm import tqdm
#from burrows_wheeler import suffix_array_best

UTF8 = 'utf-8'
CP1252 = 'cp1252'
LATIN1 = 'latin-1'
base = 256
default_char_dict = {' ': 0, 'e': 1, 't': 2, 'a': 3, 'o': 4, 'n': 5, 'i': 6, 'h': 7, 's': 8, 'r': 9, 'd': 10, 'l': 11, 'u': 12, '\r': 13, '\n': 14, 'm': 15, 'c': 16, 'w': 17, ',': 18, 'f': 19, 'g': 20, 'y': 21, 'p': 22, 'b': 23, "'": 24, '.': 25, 'v': 26, 'k': 27, 'I': 28, '-': 29, 'M': 30, 'T': 31, ';': 32, '"': 33, 'S': 34, 'A': 35, 'H': 36, '!': 37, 'W': 38, 'x': 39, 'B': 40, '?': 41, 'C': 42, 'q': 43, 'N': 44, 'P': 45, 'D': 46, 'j': 47, 'E': 48, 'L': 49, 'O': 50, 'Y': 51, 'G': 52, 'R': 53, 'F': 54, 'J': 55, 'z': 56, ':': 57, ')': 58, '(': 59, 'K': 60, 'U': 61, 'V': 62, 'Q': 63, '`': 64, '1': 65, 'X': 66, '2': 67, '0': 68, '8': 69, '3': 70, '4': 71, '5': 72, '6': 73, '7': 74, '_': 75, '*': 76, 'Z': 77, '9': 78, '&': 79, ']': 80, '[': 81, '{': 82, '}': 83, 'ï': 84, '¿': 85, '½': 86, '~': 87, '@': 88, '>': 89, '#': 90, '/': 91}

def create_dict(string, default=True):
  if default:
    return default_char_dict
  char_dict = {}
  print("Scanning through the file, getting character frequency:")
  for char in tqdm(string):
    if char in char_dict:
      char_dict[char] += 1
    else: 
      char_dict[char] = 1
  char_dict = {k: v for k, v in sorted(char_dict.items(), key=lambda item: item[1], reverse = True)}
  char_dict = [k for k in char_dict.keys()] 
  char_dict = {k:i for i, k in enumerate(char_dict)}
  return char_dict

  
# get a string and return its lempel ziv encoded string
def lz_encode(string, char_dict):
  print(f"Length of original string: {len(string)}")
  char_len = len(char_dict)
  start, end, count = 0, 0, 0
  compressed = ''

  print('LZ encoding in process:')
  for char in tqdm(string):
    count += 1
    end += 1
    if string[start: end] not in char_dict.keys():
      num = char_dict[string[start: end-1]]
      new_word_code = number_to_string(num)
      compressed += new_word_code
      char_dict[string[start: end]] = char_len
      char_len += 1
      start = end - 1
  last_word_code = number_to_string(char_dict[string[start: end]])
  compressed += last_word_code
  print(f"Length of LZ compressed string: {len(compressed)}")
  return compressed

# get a lempel ziv encoded string and write its original string to the file
def lz_decode_to_file(string, file_name, char_dict):
  with open(file_name, 'w', encoding=CP1252, newline='\n') as file:
    words_len = len(char_dict)
    count = 0
    code_word = ''
    word = ''
    words_opposite = {value: key for key, value in char_dict.items()}
    print('LZ decoding in process:')
    for char in tqdm(string):
      count += 1
      code_word += char
      if count % 3 == 0:
        num = string_to_num(code_word)
        try:
          original_word = words_opposite[num]
        except:
          original_word = word + word[0]
        file.write(original_word)
        word += original_word[0]
        if count > 3:
          words_opposite[words_len] = word
          words_len += 1
          word = original_word
        code_word = ''
  return word

# get a string and return its huffman encoded string
def huffman_encode(string):
  chars_count = {}
  words_dict = {}
  for i in range(base):
    words_dict[chr(i)] = ''
  for char in string:
    if char not in chars_count.keys():
      chars_count[char] = 1
    else:
      chars_count[char] += 1
  chars_count_sorted = sorted(chars_count.items(), key=lambda count: count[1])
  trees = [Tree(value=item) for item in chars_count_sorted]
  while len(trees) > 1:
    for char in trees[0].value[0]:
      words_dict[char] = '0' + words_dict[char]
    for char in trees[1].value[0]:
      words_dict[char] = '1' + words_dict[char]
    merge_of_chars = trees[0].value[0] + trees[1].value[0]
    sum_of_counts = trees[0].value[1] + trees[1].value[1]
    trees[1] = Tree(value=(merge_of_chars, sum_of_counts), left=trees[0], right=trees[1])
    del trees[0]
    trees = sorted(trees, key=lambda tree: tree.value[1])

  compressed_bits = ''
  compressed = ''
  count = 0
  for char in tqdm(string):
    compressed_bits += words_dict[char]
    if len(compressed_bits) > 23:
      binary = compressed_bits[:24]
      decimal = int(binary, 2)
      compressed += number_to_string(decimal)
      compressed_bits = compressed_bits[24:]
    count += 1
  if len(compressed_bits) > 0:
    compressed_bits = (compressed_bits+24*'0')[:24]
    decimal = int(compressed_bits, 2)
    compressed += number_to_string(decimal)
  separator = 3 * chr(0)
  words_dict_string = ",".join(words_dict.values())
  return words_dict_string + separator + compressed
  
# get a huffman encoded string and return its original string
def huffman_decode(string):
  separator = 3 * chr(0)
  words_dict_string = string.split(separator)[0]
  values = words_dict_string.split(",")
  words_opposite = {values[i]: chr(i) for i in range(base)}
  compressed = string.split(separator)[1]
  threshold = max([len(key) for key, value in words_opposite.items()])

  count = 0
  code_word = ''
  compressed_bits = ''
  uncompressed = ''
  print("Huffman decoding in process:")
  for char in tqdm(compressed):
    count += 1
    code_word += char
    if count % 3 == 0:
      num = string_to_num(code_word)
      binary = '{0:024b}'.format(num)
      compressed_bits += binary
      compressed_bits_index = 0
      while len(compressed_bits) >= threshold:
        compressed_bits_index += 1
        binary_word = compressed_bits[:compressed_bits_index]
        if binary_word in words_opposite.keys():
          uncompressed += words_opposite[binary_word]
          compressed_bits = compressed_bits[compressed_bits_index:]
          compressed_bits_index = 0
      code_word = ''
  compressed_bits_index = 0
  for i in range(threshold):
    compressed_bits_index += 1
    binary_word = compressed_bits[:compressed_bits_index]
    if binary_word in words_opposite.keys():
      uncompressed += words_opposite[binary_word]
      compressed_bits = compressed_bits[compressed_bits_index:]
      compressed_bits_index = 0
  return uncompressed

# get a string representation of a number (of 3 bytes)
def number_to_string(number):
  return chr(number // (base*base)) + chr(number // base % base) + chr(number % base)

# revert the string (3 characters) back to the number
def string_to_num(string):
  return ord(string[0])*base*base + ord(string[1])*base + ord(string[2])

# class for a Tree, for the huffman algorithm
class Tree:
  def __init__(self, value=None, left=None, right=None):
    self.value = value
    self.left = left
    self.right = right


def main(): 
  file_name = 'dickens.txt'
  with open(file_name, 'r', encoding=CP1252, newline='\n') as file:
    string = file.read()
  char_dict = create_dict(string, default=True)
  enc = lz_encode(string, char_dict)
  with open("encoded.txt", 'w') as file:
    file.write(enc)
  enc = huffman_encode(enc)
  print(f"Length of Huffman encoding: {len(enc)}")
  enc = huffman_decode(enc)
  dec = lz_decode_to_file(enc, "decoded.txt", char_dict)
  
main()
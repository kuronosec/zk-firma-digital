def splitToWords(number, wordsize, numberElement):
  t = number
  words = []
  baseTwo = 2
  for i in range(0, numberElement):
    words.append(t % pow(baseTwo, wordsize))
    t = t // pow(baseTwo, wordsize)
  if (t != 0):
    return None

  return words

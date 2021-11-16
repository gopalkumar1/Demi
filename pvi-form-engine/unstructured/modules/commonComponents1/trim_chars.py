def trim_chars(str, chars):
   if str.endswith(chars):
      str = str[:-len(chars)]
   if str.startswith(chars):
      str = str[len(chars):]
   return str
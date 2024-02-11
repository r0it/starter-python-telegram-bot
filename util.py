import re


ESCAPE_CHARS = "-.|()[]{}!="

def escape_asterisks(text):
  """
  Escapes single asterisks (*) that are not part of double asterisks (**).
  Preserves asterisks within single quotes, backslashes, and escaped sequences.

  Args:
    text: The string to modify.

  Returns:
    The string with escaped asterisks.
  """

  in_quotes = False
  modified_text = ""
  prev_char = ""

  for i in range(len(text)):  # iterate with an index
    char = text[i]
    if char == "'" or char == "\\":
      # Toggle in_quotes flag
      in_quotes = not in_quotes
    elif char == "*":
      if not in_quotes and prev_char != "*" and (i + 1 == len(text) or text[i + 1] != "*"):
        # Escape single asterisk if not in quotes and not part of double asterisk
        modified_text += "\\"
      modified_text += char
    else:
      modified_text += char

    prev_char = char

  return modified_text

def replace_stars(text):
  """
  Replaces double asterisks (**) with single asterisks (*) in a string.
  Leaves single asterisks unchanged.

  Args:
    text: The string to modify.

  Returns:
    The string with replaced characters.
  """

  # Replace double asterisks with single asterisks
  text = re.sub(r"\*{2}", "*", text)

  return text

def escape_markdown_data(text):
  """
  Escapes specified characters in a string with backslashes,
  ignoring already escaped characters and preserving them.
  Also replaces double asterisks with single asterisks.

  Args:
    text: The string to escape.

  Returns:
    The escaped string with original characters preserved.
  """

  text = escape_asterisks(text)
  text = replace_stars(text)  # Replace double asterisks first
  escaped_text = ""
  i = 0
  while i < len(text):
    char = text[i]
    if char == "\\":
      # Include the backslash and escape the next character if necessary
      escaped_text += char
      if i < len(text) - 1 and text[i + 1] in ESCAPE_CHARS:
        escaped_text += text[i + 1]
        i += 1
    elif char in ESCAPE_CHARS:
      # Escape only the specific characters
      escaped_text += "\\" + char
    else:
      escaped_text += char
    i += 1
  return escaped_text

# Example usage:
# text = "This is text with -special.characters| and \\escaped.\\dots."
# escaped_text = escape_markdown_data(text)
# print(escaped_text)
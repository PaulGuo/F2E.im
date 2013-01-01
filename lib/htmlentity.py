import re,htmlentitydefs

##
# Removes HTML or XML character references and entities from a text string.
#
# @param text The HTML (or XML) source text.
# @return The plain text, as a Unicode string, if necessary.

def unescape(text):
	 def fixup(m):
		  text=m.group(0)
		  if text[:2]=='&#':
				# character reference
				try:
					 if text[:3]=='&#x':
						  return unichr(int(text[3:-1],16))
					 else:
						  return unichr(int(text[2:-1]))
				except ValueError:
					 pass
		  else:
				# named entity
				try:
					 text=unichr(htmlentitydefs.name2codepoint[text[1:-1]])
				except KeyError:
					 pass
		  return text # leave as is
	 return re.sub('&#?\w+;',fixup,text)

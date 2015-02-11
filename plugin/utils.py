import vim

def error(strr):
	print(' ') # Used to display "Press ENTER to continue .."
	strr.replace("'", "\\'")
	strr.replace('"', '\\"')
	vim.command('echohl ErrorMessage')
	lines = strr.split('\n')
	for line in lines:
		vim.command('echom "' + line + '"')
	vim.command('echohl')

def bufferName(buffer):
	""" Extract the buffer name of the raw string 'buffer' """
	# Check if the buffer name is a path
	if len(buffer.split('/')) > 0:
		return buffer.split('/')[-1]
	return buffer

def del_string(string, start, end):
	""" Delete a region of a string """
	if end == -1:
		return string[:start]
	elif start == -1:
		return string[end:]
	else:
		return string[:start] + string[end:]

### The following functions are used to operate on buffers

def textPos(buf, offset):
	""" This function returns a position (x, y, flag) in the array of string 'buf' that correspond to 
	the offset 'offset' if buf was a one-dimension string (i.e. if every strings of 'buf' were concatenated) 
	The 'buf' array is assumed to be big enough !.
	'flag' indicates wether it is the end of the line (1), or the begining of the line (2) """
	x = 0
	y = 0
	flag = 0
	for i in xrange(offset):
		if x+1 == len(buf[y]):
			x = 0
			y += 1
		else:
			x += 1
	if (y == len(buf)) or (x+1 == len(buf[y])): flag = 1
	elif x == 0: flag = 2
	return (x, y, flag)

def textSubstr(buf, start, end, oneString = True, addSpace = False):
	""" Return a one-dimension string. If addSpace is True, then the function
	add one spaces between every lines (it only works if oneString is True). """
	sub = []
	if start[1] == end[1]:
		sub.append(buf[start[1]][start[0]:end[0]])
	else:
		# Else, we assume that start[1]<end[1]
		sub.append(buf[start[1]][start[0]:])
		for i in xrange(start[1] + 1, end[1] - 1):
			sub.append(buf[i])
		sub.append(buf[end[1]][:end[0]])
	if oneString:
		string = ""
		for l in sub: 
			string += l
			if addSpace:
				string += " " 
		return string
	else : return sub

def textLength(buf):
	length = 0
	for l in buf:
		length += len(l)
	return length

def textCut(buf, start, end):
	sub = textSubstr(buf, start, end, False)
	def delLine(buf, i, start, end):
		if ((end[2] == 1 and (start[0] == -1 or start[2] == 2)) or (start[2] == 2 and end[0] == -1)) : 
			del buf[i]
			return True
		else:
			buf[i] = del_string(buf[i], start[0], end[0])
			return False
	if start[1] == end[1]:
		delLine(buf, start[1], start, end)
	else:
		j = 0 # Each time we delete a line, we just decrease the index (of the following line)
		if delLine(buf, start[1], start, (-1, 0, 0)): j += 1
		for i in xrange(start[1] + 1 - j, end[1] - j):
			del buf[start[1] + 1]
			j += 1
		delLine(buf, end[1] - j, (-1, 0, 0), end)
	return sub

def textConcat(buf, add, newLine):
	""" Concat 'add' to 'buf'. The add array is assumed to be non-empty. """
	if not newLine:
		buf[-1] += add[0]
	for i in xrange(0 if newLine else 1, len(add)):
		buf.append(add[i])

def textEditLastChar(buf, newChar, append = False):
	""" If newChar is '', then this function delete the last character of the buffer. """
	y = len(buf) - 1
	if append:
		sub = buf[y]
	else:
		# Get the string without the last character
		sub = buf[y][:-1]
	buf[y] = sub + newChar

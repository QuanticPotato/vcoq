import vim

def error(strr):
	strr.replace("'", "\\'")
	strr.replace('"', '\\"')
	vim.command('echohl ErrorMessage')
	lines = strr.split('\n')
	for line in lines:
		vim.command('echom "' + line + '"')
	vim.command('echohl')

def command(cmd):
#	try:
		vim.command(cmd)
#	except vim.error as e:
#		print('Vim exception : ' + str(e))

def bufferName(buffer):
	""" Extract the buffer name of the raw string 'buffer' """
	# Check if the buffer name is a path
	if len(buffer.split('/')) > 0:
		return buffer.split('/')[-1]
	return buffer

### The following functions are used to operate on buffers

def textPos(buf, offset):
	""" This function returns a position (x, y) in the array of string 'buf' that correspond to 
	the offset 'offset' if buf was a one-dimension string (i.e. if every strings of 'buf' were concatenated) 
	The 'buf' array is assumed to be big enough ! """
	x = 0
	y = 0
	for i in xrange(offset):
		if x+1 == len(buf[y]):
			x = 0
			y += 1
		else:
			x += 1
	return (x, y)

def textSubstr(buf, start, end):
	""" Return a one-dimension string """
	if start[1] == end[1]:
		return buf[start[1]][start[0]:end[0]]
	# Then, we assume that start[1]<end[1]
	sub = buf[start[1]][start[0]:]
	for i in xrange(start[1] + 1, end[1] - 1):
		sub += buf[i]
	sub += buf[end[1]][:end[0]]
	return sub

def textLength(buf):
	length = 0
	for l in buf:
		length += len(l)
	return length

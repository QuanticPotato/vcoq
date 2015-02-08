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



import vim
import subprocess
import os
import signal

import xml.etree.ElementTree as XMLFactory

IDETabpage = None

# The following variables hold the number of the window (their position in the tabpage)
windowBuffers = {}

# The coqtop process
coqtop = None
# The string return by 'coqtop --version'
coqtopVersion = ''

def error(str):
	vim.command("echoe '" + str + "'")

def command(cmd):
	try:
		vim.command(cmd)
	except vim.error as e:
		print('Vim exception : ' + str(e))

def init(): 
	IDETabpage = vim.current.tabpage
	setupWindows()
	launchCoqtopProcess()

def createNewWindow(position, orientation, readonly, nofile, title):
	""" Create one new window, in the current tab page.
	@param position : (0=right/below, 1=left/top)  The position of the new window, compared to 
		the current window
	@param orientation : (0=horizontal, 1=vertical) The orientation of the split with the 
		current window
	@param readonly : boolean
	@param title : String
	@return : The buffer ot the new window
	"""
	orientationCmd = 'sp ' if orientation == 0 else 'vsp '
	command(orientationCmd + title)
	if position == 0: 
		vim.command('wincmd r')
	if readonly:
		vim.command('setlocal nomodifiable')
	if nofile:
		vim.command('setlocal buftype=nofile')
	return vim.current.window.buffer

def setupWindows():
	global windowBuffers
	# We first create the 3 columns, and then we split the first two, to obtain this 
	# tab page : 
	#  -------------------------------
	#  | compiled |  goals  |        |
	#  |----------|---------|        |
	#  |          | console | tagbar |
	#  |   edit   |---------|        |
	#  |          |  input  |        |
	#  -------------------------------
	#
	vim.command('e Tags')
	windowBuffers['Tagbar'] = vim.current.window.buffer
	windowBuffers['Input'] = createNewWindow(1, 1, False, True, 'Console_input')
	windowBuffers['Compiled'] = createNewWindow(1, 1, True, True, 'Accepted_statements')
	windowBuffers['Edit'] = createNewWindow(0, 0, False, False, 'Edit')
	vim.command('wincmd l')
	windowBuffers['Console'] = createNewWindow(1, 0, True, True, 'Console_output')
	windowBuffers['Goals'] = createNewWindow(1, 0, False, True, 'Goals') # Then, we resize all the windows
	command('call UpdateWindowsNumber()')
	updateWindows()

def resizeWindow(win, newSize):
	""" Resize the window 'win' (String), with 'newSize' (coordinates tuple), in percent """
	global vimWindowSize
	windowNumber = getWindowNumber(win)
	vim.windows[windowNumber].width = (float(newSize[0]) / 100.0) * float(vimWindowSize[0])
	vim.windows[windowNumber].height = (float(newSize[1]) / 100.0) * float(vimWindowSize[1])

def updateWindows():
	""" Update the size of the windows. """
	# TODO : Add variables configuration to change the window sizes.
	# By default, the windows have the following sizes :   x / y
	#	Compiled : 	40% / 35%
	#	Edit :		40% / 65%
	#	Goals : 	40% / 60%
	#	Console :	40% / 30%
	#	input :		40% / 10%
	#	Tags :		20% / 100%
	updateVimWindowSize()
	resizeWindow('Tags', (20, 100))
	resizeWindow('Compiled', (40, 35))
	resizeWindow('Goals', (40, 60))
	resizeWindow('Edit', (40, 65))
	resizeWindow('Console', (40, 30))
	resizeWindow('Input', (40, 10))

vimWindowSize = (0, 0)
def updateVimWindowSize():
	""" Update the total (all the IDE window) window size (i.e. it updates the vimWindowSize global variable"""
	global vimWindowSize
	# We assume the 5 windows (compiled, edit, goals, console and tagbar) are opened, in the right order.
	compiledWindowSize = getWindowSize('Compiled')
	goalsWindowSize = getWindowSize('Goals')
	tagbarWindowSize = getWindowSize('Tags')
	vimWindowSize = (
		compiledWindowSize[0] + goalsWindowSize[0] + tagbarWindowSize[0],
		tagbarWindowSize[1])

def getWindowNumber(win):
	""" Return the number of the window 'win' (String) """
	windowVariable = {
		'Edit' : 's:editWindow',
		'Goals' : 's:goalsWindow',
		'Console' : 's:consoleWindow',
		'Compiled' : 's:compiledWindow',
		'Tags' : 's:tagbarWindow',
		'Input' : 's:inputWindow'
	}.get(win, 'Tags')
	return int(vim.bindeval(windowVariable)) - 1

def getWindowSize(win):
	""" Return a tuple (x, y) containing the number of rows/cols of the window 'win' (String)b """
	windowNumber = getWindowNumber(win)
	return (vim.windows[windowNumber].width, vim.windows[windowNumber].height)

def launchCoqtopProcess():
	global coqtop, coqtopVersion
	if coqtop :
		try:
			coqtop.terminate()
			coqtop.communicate() 	# Clear the pipe
		except OSError:
			pass
	coqtopVersion = subprocess.check_output(['coqtop', '--version'])
	coqtop = subprocess.Popen(
			['coqtop', '-ideslave'],	# We need -ide-slave to be able to send XML queries
			stdin = subprocess.PIPE, 
			stdout = subprocess.PIPE, 
			stderr = subprocess.STDOUT,
			preexec_fn = lambda:signal.signal(signal.SIGINT, signal.SIG_IGN))
	updateWindowContent('Console', coqtopVersion)

def updateWindowContent(win, content):
	""" Clear the 'win' window, and display the 'content' string. """
	global windowBuffers
	windowBuffer = windowBuffers[win]
	readOnly = False
	if windowBuffer.options['modifiable'] == False:
		readOnly = True
		windowBuffer.options['modifiable'] = True
	del windowBuffer[:]
	lines = content.split('\n')
	windowBuffer.append(lines)
	if readOnly :
		windowBuffer.options['modifiable'] = False
	
def bufferName(buffer):
	""" Extract the buffer name of the raw string 'buffer' """
	# Check if the buffer name is a path
	if len(buffer.split('/')) > 0:
		return buffer.split('/')[-1]
	return buffer

def bufferFocusChange(entered):
	""" This function is called when the user enter or leave a buffer.
	It setup (and remove) the special maps for this buffer.
	It also perform extra actions, depending on the buffer. """
	if bufferName(vim.current.buffer.name) == 'Console_input':
		cmd = 'imap <buffer> <CR> <Esc>:py vcoq.sendQueryCommand()<CR>a' if entered else 'mapclear <buffer>'
		command(cmd)

def sendXML(xml):
	""" First, check wether the coq process is still running.
	Then it send the XML command, and finally it waits for the response """
	global coqtop
	if coqtop == None:
		error('ERROR: The coqtop process is not running or died !')
		print('Trying to relaunch it ...')
		launchCoqtopProcess()
	try:
		coqtop.stdin.write(XMLFactory.tostring(xml, 'utf-8'))
	except IOError as e:
		error('Cannot communicate with the coq process : ' + str(e))
		coqtop = None
		return None
	response = ''
	file = coqtop.stdout.fileno()
	while True:
		try:
			response += os.read(file, 0x4000)
			try:
				t = XMLFactory.fromstring(response)
				return t
			except XMLFactory.ParseError:
				continue
		except OSError:
			return None

def sendQueryCommand():
	global windowBuffers
	query = windowBuffers['Input'][0]
	xml = XMLFactory.Element('call')
	xml.set('val', 'interp')
	xml.set('id', '0')
	xml.set('raw', 'true')
	xml.text = query
	response = sendXML(xml)
	if response != None:
		if response.get('val') == 'good':

		elif response.get('val') == 'fail':


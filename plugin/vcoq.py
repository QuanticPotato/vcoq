import vim

IDETabpage = None

# The following variables hold the number of the window (their position in the tabpage)
compiledWindow = None
goalsWindow = None
tagbarWindow = None
editWindow = None
consoleWindow = None

def init(): 
	IDETabpage = vim.current.tabpage
	setupWindows()

def createNewWindow(position, orientation, readonly, title):
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
	vim.command(orientationCmd + title)
	if position == 0: 
		vim.command('wincmd r')
	# TODO : Implement the readonly param
	return vim.current.window.buffer

def setupWindows():
	# We first create the 3 columns, and then we split the first two, to obtain this 
	# tab page : 
	#  -------------------------------
	#  | compiled |  goals  |        |
	#  |----------|---------| tagbar |
	#  |   edit   | console |        |
	#  -------------------------------
	#
	vim.command('e Tags')
	tagbarWindow = vim.current.window
	goalsWindow = createNewWindow(1, 1, True, 'Goals')
	compiledWindow = createNewWindow(1, 1, True, 'Accepted_statements')
	editWindow = createNewWindow(0, 0, False, 'Edit')
	vim.command('wincmd l')
	consoleWindow = createNewWindow(0, 0, True, 'Console')
	# Then, we resize all the windows
	vim.command('call UpdateWindowsNumber()')
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
	#	Console :	40% / 40%
	#	Tags :		20% / 100%
	updateVimWindowSize()
	resizeWindow('Tags', (20, 100))
	resizeWindow('Compiled', (40, 35))
	resizeWindow('Goals', (40, 60))
	resizeWindow('Edit', (40, 65))
	resizeWindow('Console', (40, 40))

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
		'Tags' : 's:tagbarWindow'
	}.get(win, 'Tags')
	return int(vim.bindeval(windowVariable)) - 1


def getWindowSize(win):
	""" Return a tuple (x, y) containing the number of rows/cols of the window 'win' (String)b """
	windowNumber = getWindowNumber(win)
	return (vim.windows[windowNumber].width, vim.windows[windowNumber].height)

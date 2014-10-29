import vim

IDETabpage = None

# The following variables hold the buffers associated with the windows
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
	@param position : (0=right/below, 1=left/top, 2=split) The position of the new window, compared to 
		the current window
	@param orientation : (0=horizontal, 1=vertical) The orientation of the split with the 
		current window
	@param readonly : boolean
	@param title : String
	@return : The buffer ot the new window
	"""
	positionCmd = 'rightbelow' if position == 0 else 'topleft' if position == 1 else '' 
	orientationCmd = ' new ' if orientation == 0 else ' vnew '
	vim.command(positionCmd + orientationCmd + title)
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
	tagbarWindow = vim.current.window
	goalsWindow = createNewWindow(1, 1, True, 'Goals')
	consoleWindow = createNewWindow(1, 1, True, 'Console')
	compiledWindow = createNewWindow(3, 0, True, 'Accepted_statements')
	vim.command('wincmd l')
	editWindow = createNewWindow(3, 0, False, 'Edit')


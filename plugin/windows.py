import vim

class WindowsManager:

	def __init__(self):
		# The following variables hold the number of the window (their position in the tabpage)
		self.windowBuffers = {}
		self.vimWindowSize = (0, 0)

	def setupWindows(self):
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
		self.windowBuffers['Tagbar'] = vim.current.window.buffer
		self.windowBuffers['Input'] = self.createNewWindow(1, 1, False, True, 'Console_input')
		self.windowBuffers['Compiled'] = self.createNewWindow(1, 1, True, True, 'Accepted_statements')
		self.windowBuffers['Edit'] = self.createNewWindow(0, 0, False, False, 'Edit')
		vim.command('wincmd l')
		self.windowBuffers['Console'] = self.createNewWindow(1, 0, True, True, 'Console_output')
		self.windowBuffers['Goals'] = self.createNewWindow(1, 0, False, True, 'Goals') # Then, we resize all the windows
		vim.command('call UpdateWindowsNumber()')
		self.updateWindows()

	def updateVimWindowSize(self):
		""" Update the total (all the IDE window) window size (i.e. it updates the vimWindowSize global variable"""
		# We assume the 5 windows (compiled, edit, goals, console and tagbar) are opened, in the right order.
		compiledWindowSize = self.getWindowSize('Compiled')
		goalsWindowSize = self.getWindowSize('Goals')
		tagbarWindowSize = self.getWindowSize('Tags')
		self.vimWindowSize = (
			compiledWindowSize[0] + goalsWindowSize[0] + tagbarWindowSize[0],
			tagbarWindowSize[1])

	def updateWindows(self):
		""" Update the size of the windows. """
		# TODO : Add variables configuration to change the window sizes.
		# By default, the windows have the following sizes :   x / y
		#	Compiled : 	40% / 35%
		#	Edit :		40% / 65%
		#	Goals : 	40% / 60%
		#	Console :	40% / 30%
		#	input :		40% / 10%
		#	Tags :		20% / 100%
		self.updateVimWindowSize()
		self.resizeWindow('Tags', (20, 100))
		self.resizeWindow('Compiled', (40, 35))
		self.resizeWindow('Goals', (40, 60))
		self.resizeWindow('Edit', (40, 65))
		self.resizeWindow('Console', (40, 30))
		self.resizeWindow('Input', (40, 10))

	def getWindowSize(self, win):
		""" Return a tuple (x, y) containing the number of rows/cols of the window 'win' (String)b """
		windowNumber = self.getWindowNumber(win)
		return (vim.windows[windowNumber].width, vim.windows[windowNumber].height)

	def updateWindowContent(self, win, content):
		""" Clear the 'win' window, and display the 'content' string. """
		global windowBuffers
		windowBuffer = self.windowBuffers[win]
		readOnly = False
		if windowBuffer.options['modifiable'] == False:
			readOnly = True
			windowBuffer.options['modifiable'] = True
		del windowBuffer[:]
		lines = content.split('\n')
		windowBuffer.append(lines)
		if readOnly :
			windowBuffer.options['modifiable'] = False

	def createNewWindow(self, position, orientation, readonly, nofile, title):
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
		if readonly:
			vim.command('setlocal nomodifiable')
		if nofile:
			vim.command('setlocal buftype=nofile')
		return vim.current.window.buffer
	
	def resizeWindow(self, win, newSize):
		""" Resize the window 'win' (String), with 'newSize' (coordinates tuple), in percent """
		windowNumber = self.getWindowNumber(win)
		vim.windows[windowNumber].width = (float(newSize[0]) / 100.0) * float(self.vimWindowSize[0])
		vim.windows[windowNumber].height = (float(newSize[1]) / 100.0) * float(self.vimWindowSize[1])

	def getWindowNumber(self, win):
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

	def onClose(self):
		""" When a buffer is closed
		We first check if it is a Vcoq window, and then we quit if needed 
		(By the way, we update the window numbers)  (Required ?) """
		vim.command("call UpdateWindowsNumber()")


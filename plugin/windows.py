import vim

import buffers

from utils import error, textEditLastChar

class WindowsManager:

	def __init__(self, plugin):
		self.main = plugin
		self.windowsReady = False
		# The following variables hold the number of the window (their position in the tabpage)
		self.windowBuffers = {}
		self.vimWindowSize = (0, 0)
		self.input = buffers.Input(self)
		self.output = buffers.Output(self)

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
		vim.command('e __Tagbar__')
		vim.command('call InitWindow()')
		self.windowBuffers['__Tagbar__'] = vim.current.window.buffer
		self.windowBuffers['__Input__'] = self.createNewWindow(1, 1, False, '__Input__', 'Console input')
		self.windowBuffers['__Compiled__'] = self.createNewWindow(1, 1, True, '__Compiled__', 'Accepted statements')
		vim.command('setfiletype vcoq')
		self.windowBuffers['__Edit__'] = self.createNewWindow(0, 0, False, '__Edit__', 'Edit')
		vim.command('setfiletype vcoq')
		vim.command('wincmd l')
		self.windowBuffers['__Console__'] = self.createNewWindow(1, 0, True, '__Console__', 'Console output')
		self.windowBuffers['__Goals__'] = self.createNewWindow(1, 0, True, '__Goals__', "Goals") 
		self.windowsReady = True
		# Then, we resize all the windows
		self.updateWindows()

	def updateVimWindowSize(self):
		""" Update the total (all the IDE window) window size (i.e. it updates the vimWindowSize global variable"""
		# We assume the 5 windows (compiled, edit, goals, console and tagbar) are opened, in the right order.
		compiledWindowSize = self.getWindowSize('__Compiled__')
		goalsWindowSize = self.getWindowSize('__Goals__')
		tagbarWindowSize = self.getWindowSize('__Tagbar__')
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
		self.resizeWindow('__Tagbar__', (20, 100))
		self.resizeWindow('__Compiled__', (40, 35))
		self.resizeWindow('__Goals__', (40, 60))
		self.resizeWindow('__Edit__', (40, 65))
		self.resizeWindow('__Console__', (40, 30))
		self.resizeWindow('__Input__', (40, 10))

	def getWindowSize(self, win):
		""" Return a tuple (x, y) containing the number of rows/cols of the window 'win' (String)b """
		windowNumber = self.getWindowNumber(win)
		return (vim.windows[windowNumber].width, vim.windows[windowNumber].height)

	def createNewWindow(self, position, orientation, readonly, name, title):
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
		vim.command(orientationCmd + name)
		if position == 0: 
			vim.command('wincmd r')
		if readonly:
			vim.command('setlocal nomodifiable')
		vim.command("call InitWindow()")
		self.setStatusLine(title)
		return vim.current.window.buffer
	
	def resizeWindow(self, win, newSize):
		""" Resize the window 'win' (String), with 'newSize' (coordinates tuple), in percent """
		windowNumber = self.getWindowNumber(win)
		vim.windows[windowNumber].width = (float(newSize[0]) / 100.0) * float(self.vimWindowSize[0])
		vim.windows[windowNumber].height = (float(newSize[1]) / 100.0) * float(self.vimWindowSize[1])

	def getWindowNumber(self, win):
		""" Returns the number of the window 'win' (String).
		If the window cannot be found, shutdown vcoq. """
		num = int(vim.eval("bufwinnr('" + win + "')"))
		if num == -1:
			self.windowsReady = False
			self.main.shutdown()
			return
		return num - 1

	def commands(self, buf, cmds):
		""" Execute the commands 'cmds' in a specific buffer. """
		currentBuffer = vim.current.buffer.name
		vim.command("b! " + buf)
		for cmd in cmds:
			vim.command(cmd)
		vim.command("b! " + currentBuffer)

	def onEnter(self, buffer):
		""" Check if a buffer has been closed. """
		if not self.windowsReady:
			return None
		bufList = ["__Tagbar__", "__Edit__", "__Console__", "__Input__", "__Compiled__", "__Goals__"]
		for b in bufList:
			# Check if the buffer was closed
			num = int(vim.eval("bufwinnr('" + b + "')"))
			if num == -1:	
				self.windowsReady = False
				self.main.shutdown()
				return

	def setStatusLine(self, status):
		""" Update the status line of the window 'win' """
		vim.command("let &l:statusline = '" + status + "'")

	def focusWindow(self, win):
		vim.command("call FocusWindow('" + win + "')")
		


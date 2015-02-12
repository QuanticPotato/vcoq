import vim
import os

import windows as WM
import coq as CM
from file import File
from utils import error

class Plugin:

	def __init__(self):
		self.windowsManager = WM.WindowsManager(self)
		self.coqManager = CM.CoqManager(self.windowsManager)
		self.instance = None
		self.launched = False

	def launch(self): 
		# Don't relaunched if it is already running !
		if self.launched == True:
			return False
		self.launched = True
		vim.command(":call MapVcoq()")
		self.windowsManager.setupWindows()
		self.coqManager.launchCoqtopProcess()
		self.instance = File(self, (self.windowsManager.windowBuffers['__Edit__'],
			self.windowsManager.windowBuffers['__Compiled__']))
		self.windowsManager.focusWindow("__Edit__")
	
	def shutdown(self):
		self.launched = False
		error("Stopping vcoq ...")
		vim.command('windo bd') # Close every windows

	def next(self):
		if self.instance != None:
			self.instance.next()

	################
	## Vim events ##
	################

	def onBufferFocus(self, entered, buffer):
		""" This function is called when the user enter or leave a buffer.
		It setups (and removes) the special maps for this buffer.
		It also perform extra actions, depending on the buffer. """
		if self.launched == False:
			return 0
		if buffer == '__Input__':
			cmd = 'imap <buffer> <CR> <Esc>:py vcoq.main.coqManager.sendQueryCommand()<CR>a' if entered else 'mapclear <buffer>'
			vim.command(cmd)
		return 1

	def onVimResized(self):
		if self.launched == False: return 0
		self.windowsManager.updateWindows()
		return 0

	def onEnter(self, buffer):
		if self.launched == False: return 0
		self.windowsManager.onEnter(buffer)
		return 0

	def onWrite(self, filename):
		if self.launched == False: 
			error("Vcoq isn't running", prompt=False)
			return 0
		self.instance.write(filename)
		return 0

	def onOpen(self, filename):
		if self.launched == False: 
			error("Vcoq isn't running", prompt=False)
			return 0
		self.instance.open(filename)
		return 0

main = Plugin()

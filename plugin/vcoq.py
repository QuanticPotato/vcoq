import vim
import os

import windows as WM
import coq as CM
from file import File
import utils

class Plugin:

	def __init__(self):
		self.windowsManager = WM.WindowsManager()
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
		self.instance = File(self, (self.windowsManager.windowBuffers['Edit'],
			self.windowsManager.windowBuffers['Compiled']))
	
	def shutdown(self):
		self.launched = False
		# TODO : close the windows

	def next(self):
		if self.instance != None:
			self.instance.next()

	################
	## Vim events ##
	################

	def onBufferFocus(self, entered):
		""" This function is called when the user enter or leave a buffer.
		It setup (and remove) the special maps for this buffer.
		It also perform extra actions, depending on the buffer. """
		if self.launched == False:
			return False
		if utils.bufferName(vim.current.buffer.name) == 'Console_input':
			cmd = 'imap <buffer> <CR> <Esc>:py vcoq.main.coqManager.sendQueryCommand()<CR>a' if entered else 'mapclear <buffer>'
			vim.command(cmd)

	def onVimResized(self):
		if self.launched == False:
			return False
		vim.command("call UpdateWindows()")

	def onWindowsUpdated(self):
		""" Called when the windows number have been updated """
		if self.launched == False: return False
		self.windowsManager.updateWindows()

	def onClose(self):
		if self.launched == False: return False
		self.windowsManager.onClose()



main = Plugin()

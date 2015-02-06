import vim
import os

import windows as WM
import coq as CM

class Plugin:

	def __init__(self):
		self.windowsManager = WM.WindowsManager()
		self.coqManager = CM.CoqManager(self.windowsManager)
		self.launched = False

	def error(self, strr):
		strr.replace("'", "\\'")
		strr.replace('"', '\\"')
		vim.command('echohl ErrorMessage')
		lines = strr.split('\n')
		for line in lines:
			vim.command('echom "' + line + '"')
		vim.command('echohl')

	def command(self, cmd):
		try:
			vim.command(cmd)
		except vim.error as e:
			print('Vim exception : ' + str(e))

	def launch(self): 
		self.launched = True
		self.windowsManager.setupWindows()
		self.coqManager.launchCoqtopProcess()

	def bufferName(self, buffer):
		""" Extract the buffer name of the raw string 'buffer' """
		# Check if the buffer name is a path
		if len(buffer.split('/')) > 0:
			return buffer.split('/')[-1]
		return buffer

	def sendXML(self, xml):
		""" First, check wether the coq process is still running.
		Then it send the XML command, and finally it waits for the response """
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

	################
	## Vim events ##
	################

	def onBufferFocus(self, entered):
		""" This function is called when the user enter or leave a buffer.
		It setup (and remove) the special maps for this buffer.
		It also perform extra actions, depending on the buffer. """
		if self.launched == False:
			return False
		if self.bufferName(vim.current.buffer.name) == 'Console_input':
			cmd = 'imap <buffer> <CR> <Esc>:py vcoq.main.coqManager.sendQueryCommand()<CR>a' if entered else 'mapclear <buffer>'
			self.command(cmd)

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

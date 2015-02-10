from utils import textConcat, textCut, textEditLastChar

class File:
	""" Represents a file (A separated class allow to open several files at a time.
	The class also holds the whole file content. (The vim buffers only store either the
	accepted chunks, or the editing statement) """

	def __init__(self, plugin, buffers):
		self.windowsManager = plugin.windowsManager
		self.coqManager = plugin.coqManager
		self.input = buffers[0]
		self.output = buffers[1]
		# The whole file content
		self.code = []
		self.editPosition = (0, 0)
		# We manage a virtual new-line at the end of the compiled buffer.
		self.editNewLine = False
		self.output.options['modifiable'] = True
		self.windowsManager.commands('Accepted_statements', ["normal iPR"])
		self.output.options['modifiable'] = False
		# Each chunk is describe by the following tuple : (startPos, endPos), where startPos and endPos are coords tuple
		self.chunks = []

	def next(self):
		nextChunk = self.windowsManager.input.getChunk(self.input, (0, 0))
		if nextChunk :
			if self.coqManager.sendChunk(nextChunk[0]):
				chunk = textCut(self.input, (0, 0, 2), nextChunk[1])
				print(chunk)
				self.output.options['modifiable'] = True
				# Remove the last newline-cursor
				self.windowsManager.commands('Accepted_statements', ["normal G$a"])
				textConcat(self.output, chunk, self.editNewLine)
				self.editNewLine = nextChunk[2]
				if self.editNewLine:
					self.windowsManager.commands('Accepted_statements', ["normal G$aDt"])
				else:
					self.windowsManager.commands('Accepted_statements', ["normal G$aPR"])
				self.output.options['modifiable'] = False
	def sync(self):
		""" Update self.code starting from self.editPosition, with the Edit buffer content """
		
		

	

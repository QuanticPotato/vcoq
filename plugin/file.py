from utils import textConcat, textCut

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
		self.editNewLine = True
		# Each chunk is describe by the following tuple : (startPos, endPos), where startPos and endPos are coords tuple
		self.chunks = []

	def next(self):
		nextChunk = self.windowsManager.input.getChunk(self.input, (0, 0))
		if nextChunk :
			if self.coqManager.sendChunk(nextChunk[0]):
				chunk = textCut(self.input, (0, 0, 2), nextChunk[1])
				self.output.options['modifiable'] = True
				textConcat(self.output, chunk, self.editNewLine)
				self.output.options['modifiable'] = False

	def sync(self):
		""" Update self.code starting from self.editPosition, with the Edit buffer content """
		
		

	

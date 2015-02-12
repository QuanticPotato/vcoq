from utils import textConcat, textCut, textEditLastChar, error, textCursorPos

class File:
	""" Represents a file (A separated class allow to open several files at a time.
	The class also holds the whole file content. (The vim buffers only store either the
	accepted chunks, or the editing statement) """

	def __init__(self, plugin, buffers):
		self.windowsManager = plugin.windowsManager
		self.coqManager = plugin.coqManager
		self.input = buffers[0]
		self.output = buffers[1]
		# Each chunk is describe by the following tuple : (startPos, endPos), where startPos and endPos are coords tuple
		self.chunks = []
		# The whole file content
		self.code = []
		self.editPosition = (0, 0)
		# We manage a virtual new-line at the end of the compiled buffer.
		self.initOutputCursor()
		
	def initOutputCursor(self):
		""" Init the newline-cursor in the Compiled buffer. """
		self.output.options['modifiable'] = True
		del self.output[:]
		self.windowsManager.commands('__Compiled__', ["normal i PR"])
		self.output.options['modifiable'] = False
		self.editNewLine = False
		# We backtrack every chunks
		self.chunks = self.chunks[:- self.coqManager.rewind(len(self.chunks))]

	def next(self):
		nextChunk = self.windowsManager.input.getChunk(self.input, (0, 0))
		if nextChunk :
			if self.coqManager.sendChunk(nextChunk[0]):
				if self.editNewLine:
					chunkStart = (0, textCursorPos(self.output)[1] + 1)
				else:
					chunkStart = textCursorPos(self.output, diffX = 3) # diffX=2 to ignore the newline-cursor
				chunk = textCut(self.input, (0, 0, 2), nextChunk[1])
				self.output.options['modifiable'] = True
				# Remove the last newline-cursor
				self.windowsManager.commands('__Compiled__', ["normal G$a"])
				textConcat(self.output, chunk, self.editNewLine)
				self.editNewLine = nextChunk[2]
				chunkEnd = textCursorPos(self.output)
				if self.editNewLine:
					self.windowsManager.commands('__Compiled__', ["normal G$a Dt"])
				else:
					self.windowsManager.commands('__Compiled__', ["normal G$a PR"])
				self.output.options['modifiable'] = False
				self.chunks.append((chunkStart, chunkEnd))

	def write(self, filename):
		try:
			file = open(filename, 'w')
			# We write the compiled buffer, and then the edit buffer
			for i in xrange(len(self.output) - 1):
				file.write(self.output[i] + "\n")
			interline = self.output[-1][:-4] # We don't take the newline-cursor
			if not self.editNewLine:
				interline += self.input[0]
			file.write(interline + "\n")
			for i in xrange(0 if self.editNewLine else 1, len(self.input)):
				file.write(self.input[i] + "\n")
			file.close()
		except IOError as e:
			error(str(e))

	def open(self, filename):
		# First, clear the buffers
		self.initOutputCursor()
		del self.chunks[:]
		del self.input[:]
		try:
			file = open(filename, 'r')
			# We simply add every lines in the Edit buffer
			firstLine = True
			for line in file:
				if firstLine: # We don't want to skip the first line
					self.input[0] = line
					firstLine = False
				else: self.input.append(line)
			file.close()
		except IOError as e:
			error(str(e))

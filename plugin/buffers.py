from enum import Enum

class Color(Enum):
	""" Each of the following colors correspond to a vim highlight. """
	default = 0
	#########################################
	#  python  	#  Vim highlight code 	#
	#		# (defined in vcoq.vim) #
	red = 1  	#	Red		# 
	blue = 2	#	Blue		#
	yellow = 3	#	Yellow		#
	white = 4	#	White		#
	green = 5	#	Green		#
	purple = 6	#	Purple		#
	#########################################

class Text:
	""" This class describes a text portion (Content, color ..) """

	def __init__(self, txt):
		""" txt is a classical string """
		self.content = txt.split('\n')
		# The text position (i.e. where the text is blit in the vim buffer)
		self.position = (0, 0)
		# A list that gives every color regions. Each region is described with a tuple : 
		# (posX, posY, length, Color)
		self.colors = [(0, 0, len(txt), Color.default)]
	
	def setColor(self, col):
		""" This function colors the whole content """
		self.colors = [(0, 0, self.length(), Color.default)]

	def setPosition(self, x, y):
		self.position = (x, y)

	def length(self):
		""" Returns the content length """
		contentLength = 0
		for l in self.content:
			contentLength += len(l)
		return contentLength

	def lines(self):
		""" Returns the affected lines (with their bounds). For example :
		(5, "te") corresponds to the line :  ......te............ .. .. """
		lines = []
		for l in self.content:
			lines.append((self.position[0], l))
		return lines

	def colorAt(self, x, y):
		""" Returns the first color that contains the point (x, y).
		If the point (x, y) is not present in the color regions, then Color.default is returned. """
		for color in self.colors:
			if color[1] == y:
				if(x >= color[0]  and x <= (color[0] + color[2])) :
					return color[3]
		return Color.default

class Input:
	## The functions in this class read a window buffer and extract a certain area.
	
	def __init__(self, wm):
		self.windowsManager = wm

	def getLine(self, bufName, num):
		""" num : the line number """
		return self.windowsManager.windowBuffers[bufName][num]

class Output:
	## This class manage the dynamic highlighting

	def __init__(self, wm):
		self.windowsManager = wm
		# The class maintains an array (with the same size that the buffers),
		# to store every character color
		# (Each entry is initialized at the first call of updateWindowContent)
		self.colors = {}

	def updateWindowContent(self, win, content, clear=False):
		""" Update the region described by 'content' (it must be a 'Text' object) in the 'win' window 
		This function only works with non-modifiable buffer ! """
		windowBuffer = self.windowsManager.windowBuffers[win]
		if windowBuffer.options['modifiable'] == True:
			return False
		windowBuffer.options['modifiable'] = True
		if (not win in self.colors) or clear :
			del windowBuffer[:]
			self.colors[win] = []
		lines = content.lines()
		for i in xrange(len(lines)):
			y = i + content.position[1]
			l = lines[i]

			# Add lines if needed
			while len(windowBuffer) <= y:
				windowBuffer.append(" ")
			while len(self.colors[win]) <= y:
				self.colors[win].append([Color.default])
				
			lineStart = windowBuffer[y][:l[0]]
			# Add extra spaces if the former line was shorter than the new one
			lineStart += (l[0] - len(lineStart))*" "
			windowBuffer[y] = lineStart + l[1]

			# Extend the colors array if needed (with default color)
			while len(self.colors[win][y]) < (l[0] + len(l[1])):
				self.colors[win][y].extend([Color.default])
				
			# And finaly update the color of the affected region of the text
			for j in xrange(len(l[1])):
				self.colors[win][y][l[0] + j] = content.colorAt(j, i)

		windowBuffer.options['modifiable'] = False

	#def updateHighlight(self):



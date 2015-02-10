from enum import Enum

from utils import textPos, textSubstr, textLength

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

	def getLine(self, bufName, line):
		""" Returns the 'line' line from the 'bufName' buffer (without the trailling '\n' """
		return self.windowsManager.windowBuffers[bufName][line]

	def getChunk(self, buf, fromPos):
		""" Return either :
			- The code between 'from' (a tuple (x, y)) and the next dot 
			- The next comment
		The dots included in comments, strings or in import path, and the nested comments  are ignored. 
		Returns the chunk in a string, and the end position of the chunk in the buffer, or False if it fails """
		# First, we switch depending on the next chunk type
		relevantPos = self.skipWhitespaces(buf, fromPos)
		if relevantPos == (-1, 1):
			print("Buffer is empty !")
			return False
		elif relevantPos == (-1, 2):
			# Only whitespaces ..
			return False
		(remaining, skipped) = self.remainingContent(buf, relevantPos)
		if remaining[:2] == "(*":
			commentEnd = self.skipCommentBuf(buf, relevantPos)
			if commentEnd == (-1, 3):
				print("Unterminated comment !")
				return False
			chunk = textSubstr(buf, fromPos, commentEnd)
			return (chunk, textPos(buf, len(chunk)))
		else:
			# If it's not a comment, we try to reach the next *relevant* point (i.e. ignoring comments, strings and import paths)
			dotPos = 0
			while dotPos < (textLength(buf) - skipped):
				comment_occ = remaining.find("(*", dotPos)
				string_occ = remaining.find("\"", dotPos)
				dot_occ = remaining.find(".", dotPos)
				if dot_occ == -1:
					print("No ending dot !")
					return False
				if(comment_occ != -1 and (string_occ == -1 or comment_occ < string_occ) and comment_occ < dot_occ):
					commentEnd = self.skipComment(remaining, comment_occ)
					if commentEnd == -1:
						print("Unterminated comment !")
					dotPos = commentEnd
				elif(string_occ != -1 and (comment_occ == -1 or string_occ < comment_occ) and string_occ < dot_occ):
					dotPos = remaining.find("\"", string_occ + 1) + 1
					if dotPos == 0: # /!\ Not -1 because we added 1 !
						print("Unterminated string !")
						return False
				else: 
					# A dot is relevant only if it is followed by a space, or if it is the last character of the line
					dotPosInBuf = textPos(buf, skipped + dot_occ + 2)
					if (remaining[dot_occ + 1:dot_occ + 1].strip() == "") or (dotPosInBuf[0] + 1 == len(buf[dotPosInBuf[1]])):
						chunkEndPos = textPos(buf, skipped + len(remaining[:dot_occ]) + 1)
						chunkEndPos = (chunkEndPos[0] + 1, chunkEndPos[1], chunkEndPos[2])
						chunk = textSubstr(buf, (0, 0), chunkEndPos, True, True)
						newLine = chunkEndPos[0] == len(buf[chunkEndPos[1]])
						return (chunk, chunkEndPos, newLine)
					else:
						dotPos = dot_occ + 1
			print("No ending dot !")
			return False

	def remainingContent(self, buf, fromPos):
		""" Returns the remaining characters after the given position (x, y) 
		(in one string), and the number of skipped characters """
		skipped = 0
		for i in xrange(fromPos[1]):
			skipped += len(buf[i])
		remaining = buf[fromPos[1]][fromPos[0]:]
		skipped += fromPos[0] - 1
		for i in xrange(fromPos[1] + 1, len(buf)):
			remaining += buf[i]
		return (remaining, skipped)

	# The following functions skip  whitespaces, comments and strings from the 'fromPos' position given. 
	# They return the new *relevant* position. 
	# If an error is detected, the functions return a tuple (-1, errCode), where errCode is one of the following :
	#		- 1: Empty bufer (no characters)
	#		- 2: Empty buffer (only whitespaces)
	#		- 3: Unterminated comment

	def skipWhitespaces(self, buf, fromPos):
		if len(buf) == 0 or (len(buf) == 1 and len(buf[0]) == 0):
			return (-1, 1)
		i = fromPos[1]
		relevantPosFound = False
		relevantPos = (-1, -1)
		while i<len(buf) and not relevantPosFound: 
			for j in xrange(fromPos[0] if i==fromPos[1] else 0, len(buf[i])):
				if buf[i][j].strip() != '':
					relevantPos = (j, i)
					relevantPosFound = True
					break
			i += 1
		# If relevantPos==(-1, -1), then there are only whitespaces remaining ..
		if relevantPos == (-1, -1):
			return (-1, 2)
		return relevantPos

	def skipCommentBuf(self, buf, fromPos):
		relevantPos = fromPos
		(remaining, skipped) = self.remainingContent(buf, relevantPos)
		endComment = self.skipComment(remaining, 0)
		if endComment == -1:
			return (-1, 3) # Unterminated comment
		relevantPos = textPos(buf, skipped + endComment + 1) 
		return relevantPos

	def skipComment(self, string, fromPos):
		# If there are several comments nested, we use a stack
		endComment = fromPos + 1
		stack = 1
		while stack > 0 and endComment < len(string):
			start_occ = string.find("(*", endComment)
			end_occ = string.find("*)", endComment)
			if end_occ > -1:
				if start_occ != -1 and start_occ < end_occ:
					stack += 1
					endComment = start_occ + 2
				else:
					stack -= 1
					endComment = end_occ + 2
			else: break
		# If stack is not 0, then the remaining code is only comment ...
		if stack > 0:
			return -1
		return endComment

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



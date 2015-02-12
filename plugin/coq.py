import xml.etree.ElementTree as XMLFactory
import subprocess
import os
import signal

import utils
from buffers import Text, Color

class CoqManager:
	
	def __init__(self, WM):
		# The coqtop process
		self.coqtop = None
		# The string return by 'coqtop --version'
		self.coqtopVersion = ''
		# The windows manager instance
		self.windowsManager = WM

	def launchCoqtopProcess(self):
		if self.coqtop :
			try:
				self.coqtop.terminate()
				self.coqtop.communicate() 	# Clear the pipe
			except OSError:
				pass
		self.coqtopVersion = subprocess.check_output(['coqtop', '--version'])
		self.coqtop = subprocess.Popen(
				['coqtop', '-ideslave'],	# We need -ide-slave to be able to send XML queries
				stdin = subprocess.PIPE, 
				stdout = subprocess.PIPE, 
				stderr = subprocess.STDOUT,
				preexec_fn = lambda:signal.signal(signal.SIGINT, signal.SIG_IGN))
		versionText = Text(self.coqtopVersion)
		versionText.setPosition(0, 2)
		self.windowsManager.output.updateWindowContent('__Console__', versionText)

	def sendQueryCommand(self):
		query = self.windowsManager.input.getLine("__Input__", 0)
		xml = XMLFactory.Element('call')
		xml.set('val', 'interp')
		xml.set('id', '0')
		xml.set('raw', 'true')
		xml.text = query
		response = self.sendXML(xml)
		if response != None:
			if response.get('val') == 'good':
				response_info = response.find('string')
				if not response_info is None:
					rep = Text(response_info.text)
					self.windowsManager.output.updateWindowContent("__Console__", rep, True)
			elif response.get('val') == 'fail':
				err = Text(str(response.text))
				err.setColor(Color.red)
				self.windowsManager.output.updateWindowContent("__Console__", err, True)
		else:
			utils.error("No responses (query) ..")

	def sendChunk(self, chunk):
		xml = XMLFactory.Element('call')
		xml.set('val', 'interp')
		xml.set('id', '0')
		xml.text = chunk.decode('utf-8')
		response = self.sendXML(xml)
		if response != None:
			if response.get('val') == 'good':
				#response_info = response.find('string')
				#if not response_info is None:
				#	rep = Text(response_info.text)
				#	self.windowsManager.output.updateWindowContent("Console", rep, True)
				return True
			elif response.get('val') == 'fail':
				err = Text(str(response.text))
				err.setColor(Color.red)
				self.windowsManager.output.updateWindowContent("__Console__", err, True)
		else:
			utils.error("No responses (sendChunk) ..")
		return False

	def rewind(self, steps):
		xml = XMLFactory.Element('call')
		xml.set('val', 'rewind')
		xml.set('steps', str(steps))
		response = self.sendXML(xml)
		if response != None:
			if response.get('val') == 'good':
				additional_steps = response.find('int')
				return steps + int(additional_steps.text)
			print(XMLFactory.tostring(response))
			utils.error("Something went wrong !")
		else:
			utils.error("No responses (rewind) ..")
		return 0

	def sendXML(self, xml):
		""" First, check wether the coq process is still running.
		Then it send the XML command, and finally it waits for the response """
		if self.coqtop == None:
			utils.error('ERROR: The coqtop process is not running or died !')
			print('Trying to relaunch it ...')
			self.launchCoqtopProcess()
		try:
			self.coqtop.stdin.write(XMLFactory.tostring(xml, 'utf-8'))
		except IOError as e:
			utils.error('Cannot communicate with the coq process : ' + str(e))
			self.coqtop = None
			return None
		response = ''
		file = self.coqtop.stdout.fileno()
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



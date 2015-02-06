import xml.etree.ElementTree as XMLFactory
import subprocess
import os
import signal

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
		self.windowsManager.updateWindowContent('Console', self.coqtopVersion)

	def sendQueryCommand(self):
		query = windowBuffers['Input'][0]
		xml = XMLFactory.Element('call')
		xml.set('val', 'interp')
		xml.set('id', '0')
		xml.set('raw', 'true')
		xml.text = query
		response = sendXML(xml)
		if response != None:
			if response.get('val') == 'good':
				print(response.find('string').text)
			elif response.get('val') == 'fail':
				error(str(response.text))
		else:
			error("No responses ..")

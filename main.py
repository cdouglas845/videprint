import logging
import sys
import time
import traceback

from optparse import OptionParser

from models.datafeeds.bbcevent import BbcEventFeed
from controllers.videprint import VidePrinter

class Main(object):

	OUTPUT_TYPE_BASIC = 'BASIC'
	OUTPUT_TYPE_UI    = 'UI'

	def __init__(self):
		self._bolFullReplay = False
		self._outputType    = self.OUTPUT_TYPE_UI
		self.objLogger = self.getLogger()
		self._parseOptions()
		self.objFeed = BbcEventFeed()

	def setFullReplay(self, bolFullReplay):
		self._bolFullReplay = bolFullReplay

	def needsFullReplay(self):
		return self._bolFullReplay

	def setBasicOutput(self):
		self._outputType = self.OUTPUT_TYPE_BASIC

	def getOutputType(self):
		return self._outputType

	def getLogger(self):
		# Will normally exist, so this is faster
		# than checking if the attribute exists first
		try:
			return self.objLogger

		except AttributeError:
			objLogger    = logging.getLogger('videprinter')
			objHdlr      = logging.FileHandler('/var/log/videprinter.log')
			objFormatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')

			objHdlr.setFormatter(objFormatter)
			objLogger.addHandler(objHdlr)
			objLogger.setLevel(logging.INFO)
			return objLogger

	def _parseOptions(self):
		parser = OptionParser()

		parser.add_option('-r', '--replay',
		                  action='store_true', dest='bolFullReplay', default=False,
		                  help='Perform a full replay of all events on feed')

		parser.add_option('-b', '--basic',
		                  action='store_true', dest='bolBasicOutput', default=False,
		                  help='Use the basic stdout display rather than the UI')

		(objOptions, dctArgs) = parser.parse_args()

		self.setFullReplay(objOptions.bolFullReplay)

		if objOptions.bolBasicOutput:
			self.setBasicOutput()

	def addTerminalPrinter(self):
		from views.termprint import TerminalOutput

		objOutput = TerminalOutput()
		objVide = VidePrinter(self.objFeed, objOutput, self.getLogger())
		if self.needsFullReplay():
			objVide.enableReplay()
		objVide.start()

		# bit hacky, but exit on a keypress for now
		try:
			sys.stdin.read(1)
		except:
			self.getLogger().error(traceback.format_exc())
		finally:
			objVide.stop()

	def addTerminalUi(self):
		from views.termui import TerminalUi

		try:
			objOutput = TerminalUi()
			objVideOutput = objOutput.addScrollRegion(10, 70, 0, 0)
			objVide = VidePrinter(self.objFeed, objVideOutput, self.getLogger())
			if self.needsFullReplay():
				objVide.enableReplay()
			objVide.start()
		except:
			objLogger.error(traceback.format_exc())
			if 'objVide' in locals():
				objVide.stop()
			if 'objOutput' in locals():
				objOutput.__del__()
				del objOutput
			sys.exit()

		# bit hacky, but exit on a keypress for now
		try:
			objOutput.objScreen.getch()
		except:
			objLogger.error(traceback.format_exc())
		finally:
			objVide.stop()

	def start(self):
		if self.getOutputType() == self.OUTPUT_TYPE_UI:
			self.addTerminalUi()
		else:
			self.addTerminalPrinter()

if __name__ == '__main__':
	objMain = Main()
	objMain.start()

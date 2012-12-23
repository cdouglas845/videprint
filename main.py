import logging
import sys
import time
import traceback

from optparse import OptionParser

from models.datafeeds.bbcevent import BbcEventFeed
from controllers.videprint import VidePrinter

class Main(object):

	def __init__(self):
		self._bolFullReplay = False
		self.objLogger = self.getLogger()
		self._parseOptions()
		self.objFeed = BbcEventFeed()

	def setFullReplay(self, bolFullReplay):
		self._bolFullReplay = bolFullReplay

	def needsFullReplay(self):
		return self._bolFullReplay

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

		(objOptions, dctArgs) = parser.parse_args()

		self.setFullReplay(objOptions.bolFullReplay)

	def addTerminalPrinter(self):
		from views.termprint import TerminalOutput

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
		self.addTerminalUi()

if __name__ == '__main__':
	objMain = Main()
	objMain.start()

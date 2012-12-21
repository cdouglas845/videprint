import logging
import sys
import time
import traceback

#from views.termprint import TerminalOutput
from views.termui import TerminalUi
from models.datafeeds.bbcevent import BbcEventFeed
from controllers.videprint import VidePrinter


# Setup logger
# TODO: Tidy this shite up
objLogger    = logging.getLogger('videprinter')
objHdlr      = logging.FileHandler('/var/log/videprinter.log')
objFormatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
objHdlr.setFormatter(objFormatter)
objLogger.addHandler(objHdlr)
objLogger.setLevel(logging.INFO)



objFeed = BbcEventFeed()
#objFeed2 = BbcEventFeed()
#objOutput = TerminalOutput()

try:
	objOutput = TerminalUi()
	objVideOutput = objOutput.addScrollRegion(10, 70, 0, 0)
	objVide = VidePrinter(objFeed, objVideOutput, objLogger)
	objVide.start()
#	time.sleep(2)
#	objVideOutput2 = objOutput.addScrollRegion(10, 70, 0, 10)
#	objVide2 = VidePrinter(objFeed2, objVideOutput2, objLogger)
#	objVide2.start()
except:
	objLogger.error(traceback.format_exc())
	if 'objVide' in locals():
		objVide.stop()
#		objVide2.stop()
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
#	objVide2.stop()

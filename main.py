import logging
import sys
import time
import traceback

from optparse import OptionParser

#from views.termprint import TerminalOutput
from views.termui import TerminalUi
from models.datafeeds.bbcevent import BbcEventFeed
from controllers.videprint import VidePrinter


# Setup logger
# TODO: Tidy this up
objLogger    = logging.getLogger('videprinter')
objHdlr      = logging.FileHandler('/var/log/videprinter.log')
objFormatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')

objHdlr.setFormatter(objFormatter)
objLogger.addHandler(objHdlr)
objLogger.setLevel(logging.INFO)

parser = OptionParser()
parser.add_option('-r', '--replay',
                  action='store_true', dest='bolReplay', default=False,
                  help='Perform a full replay of all events on feed')

(dctOptions, dctArgs) = parser.parse_args()

objFeed = BbcEventFeed()

try:
	objOutput = TerminalUi()
	objVideOutput = objOutput.addScrollRegion(10, 70, 0, 0)
	objVide = VidePrinter(objFeed, objVideOutput, objLogger)
	if dctOptions.bolReplay:
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

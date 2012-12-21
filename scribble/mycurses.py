import curses
import time
from ..views import termui

def mainui(myscreen):
	myscreen.refresh()

	objVide = termui.ScrollRegion(myscreen, 10, 40, 226, 43)

	#(vidwin, vidpad) = addScrollRegion(12, 62, 10, 10)

	for x in range(1, 40):
		objVide.addLine("new line {0}".format(x))
		time.sleep(0.2)

	myscreen.getch()
	curses.endwin()

# Catches any exceptions and leaves term usable
curses.wrapper(mainui)

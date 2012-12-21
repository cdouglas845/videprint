import curses
import time
import threading

class TerminalUi:
	def __init__(self):
		self.objScreen = curses.initscr()
		self.__initColours()
		curses.noecho()
		curses.cbreak()
		self.objScreen.keypad(1)
		self.objScreen.refresh()
		self.__objDefaultOutput = None
		self.__objLock = threading.Lock()

	# Due to the nature of curses, we need to tidy up
	# and due to the way we're using the curses objects
	# we can't just use the wrapper
	# If we don't tidy up, the terminal will be unusable
	def __del__(self):
		self.cleanup()

	@property
	def objLock(self):
		return self.__objLock

	def cleanup(self):
		self.objScreen.erase()
		self.objScreen.refresh()
		self.objScreen.keypad(0)
		curses.echo()
		curses.nocbreak()
		curses.endwin()

	def __initColours(self):
		curses.start_color()
		curses.init_pair(1, curses.COLOR_RED,   curses.COLOR_BLACK)
		curses.init_pair(2, curses.COLOR_GREEN, curses.COLOR_BLACK)
		curses.init_pair(3, curses.COLOR_YELLOW, curses.COLOR_BLACK)
		curses.init_pair(5, curses.COLOR_MAGENTA, curses.COLOR_BLACK)
		curses.init_pair(6, curses.COLOR_CYAN, curses.COLOR_BLACK)

	def addScrollRegion(self, intLines, intWidth, intX, intY):
		return ScrollRegion(self, self.objScreen, intLines, intWidth, intX, intY)

	def addStaticRegion(self, intLines, intWidth, intX, intY):
		return StaticRegion(self, self.objScreen, intLines, intWidth, intX, intY)

# Base class to derive "Regions" from
class Region(object):
	C_PURPLE = 5
	C_BLUE   = 6
	C_GREEN  = 2
	C_YELLOW = 3
	C_RED    = 1
	C_END    = 0

	def __init__(self, objParent, objScreen, intLines, intWidth, intX=0, intY=0):
		self.objParent = objParent
		self.__checkParams(objScreen, intLines, intWidth, intX, intY)
		self.__intViewLines = intLines - 2
		self.__intViewWidth = intWidth - 2
		(self.__objWin, self.__objPad) = self.__addRegion(intLines, intWidth, intX, intY)

	@property
	def intViewLines(self):
		return self.__intViewLines

	@property
	def intViewWidth(self):
		return self.__intViewWidth

	@property
	def objPad(self):
		return self.__objPad

	def __checkParams(self, objScreen, intLines, intWidth, x, y):
		(intScreenMaxY, intScreenMaxX) = objScreen.getmaxyx()

		if x < 0 or x + intWidth > intScreenMaxX:
			raise OutOfRangeError(x, 0, intScreenMaxX - intWidth)

		if y < 0 or y + intLines > intScreenMaxY:
			raise OutOfRangeError(y, 0, intScreenMaxY - intLines)

	# Convenience method, returns (win, pad)
	def __addRegion(self, lines, width, x=0, y=0):
		self.objParent.objLock.acquire()
		win = curses.newwin(lines, width, y, x)
		win.border()
		win.refresh()
		pad = curses.newpad(lines-2, width-2) # Allow for border of win
		pad.refresh(0, 0, y+1, x+1, y+self.intViewLines-1, x+width)
		self.objParent.objLock.release()
		return (win, pad)

	# Refresh viewable area
	def refresh(self):
		self.objParent.objLock.acquire()
		pad = self.__objPad
		(y, x) = pad.getbegyx()
		(height, width) = pad.getmaxyx()
		pad.refresh(height-self.intViewLines, 0, y, x, y+self.intViewLines-1, x+width)
		self.objParent.objLock.release()

class StaticRegion(Region):
	def __init__(self, objParent, objScreen, intLines, intWidth, intX=0, intY=0):
		super(StaticRegion, self).__init__(objParent, objScreen, intLines, intWidth, intX, intY)

# Nice wrapper for adding scrolling regions
class ScrollRegion(Region):
	def __init__(self, objParent, objScreen, intLines, intWidth, intX=0, intY=0):
		super(ScrollRegion, self).__init__(objParent, objScreen, intLines, intWidth, intX, intY)

	# Convenience method to add a line to the bottom and scroll
	def addLine(self, lstLine):
		pad = self.objPad
		(y, x) = pad.getbegyx()
		(height, width) = pad.getmaxyx()
		pad.resize(height+1, width)

		intChunkX = 0
		for tupChunk in lstLine:
			intChunkX = self.addText(height, intChunkX, tupChunk[0], tupChunk[1])

	def addText(self, intY, intX, strText, intColourPair):
		for strChar in strText:
			self.addChar(intY, intX, strChar, intColourPair)
			intX += 1
		return intX

	def addChar(self, intY, intX, strChar, intColourPair):
		self.objParent.objLock.acquire()
		self.objPad.addstr(intY, intX, strChar, curses.color_pair(intColourPair))
		self.objParent.objLock.release()
		self.refresh()
		time.sleep(0.02)


class OutOfRangeError(Exception):
	def __init__(self, intValue, intMin, intMax):
		strMsg = "Value '{0}' is out of range, must be between '{1}' and '{2}'"
		self.msg = strMsg.format(intValue, intMin, intMax)
	def __str__(self):
		return self.msg

if __name__ == '__main__':

	def mainui(myscreen):
		myscreen.refresh()

		objVide = ScrollRegion(myscreen, 10, 40, 0, 0)
		objVid2 = ScrollRegion(myscreen, 10, 40, 40, 0)
		objVid3 = ScrollRegion(myscreen, 10, 80, 0, 10)

		#(vidwin, vidpad) = addScrollRegion(12, 62, 10, 10)

		for x in range(1, 40):
			objVide.addLine("new line {0}".format(x))
			objVid2.addLine("new line {0}".format(40-x))
			objVid3.addLine("wide screen line {0}".format(x))
			time.sleep(0.2)

		myscreen.getch()
		curses.endwin()

	# Catches any exceptions and leaves term usable
	curses.wrapper(mainui)

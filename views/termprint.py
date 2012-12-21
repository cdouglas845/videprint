import sys
import time

class TerminalOutput:
	C_PURPLE = '\033[95m'
	C_BLUE   = '\033[94m'
	C_GREEN  = '\033[92m'
	C_YELLOW = '\033[93m'
	C_RED    = '\033[91m'
	C_END    = '\033[0m'

	# lstLine is a list of (strText, strColour) tuples
	# where strColour is a class constant
	# decCharDelay is the time delay between outputting characters
	def addLine(self, lstLine, decCharDelay=0.02):
		# Build the whole line
		for tupChunk in lstLine:
			sys.stdout.write(tupChunk[1])
			for strChar in tupChunk[0]:
				sys.stdout.write(strChar)
				sys.stdout.flush()
				time.sleep(decCharDelay)
		print TerminalOutput.C_END

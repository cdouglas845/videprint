import time
import threading
import traceback

from models.matchevent import MatchEvent

# Designed to run its own thread to allow multiple feeds
# TODO: The output methods _really_ need separating out,
#       currently its far too tightly coupled
class VidePrinter(threading.Thread):

	intFirstRunMaxEvents = 5

	def __init__(self, objFeed, objOutput, objLogger):
		self.__objStop     = threading.Event()
		self._strLastEvent = None
		self._bolReplay    = False
		self.objFeed       = objFeed
		self.objOutput     = objOutput
		self.objLogger     = objLogger
		super(VidePrinter, self).__init__()

	def stop(self):
		self.__objStop.set()
		self.join()

	def enableReplay(self):
		self._bolReplay = True

	def getLastEvent(self):
		return self._strLastEvent

	def outputEvent(self, e):
		fncOutput = getattr(self, '_output_' + e.strEventType, None)

		if callable(fncOutput):
			fncOutput(e)
		else:
			# Unknown eventType found, log the error
			self.objLogger.error('VidePrinter encountered an unknown event type: ' + e.strEventType)
		self._strLastEvent = e.strUniqueId

	def _output_DISMISSAL(self, e):
		strTeam = e.strHomeTeam if e.bolHomeTeam else e.strAwayTeam
		lstLine = []
		lstLine.append(('OFF: ', self.objOutput.C_RED))
		lstLine.append(('{player} ({team}) '.format(player=e.strPlayer, team=strTeam), self.objOutput.C_RED))
		lstLine.append((' - {comment} {mins}\''.format(comment=e.strComment, mins=e.intMins), self.objOutput.C_END))
		self.objOutput.addLine(lstLine)

	def _output_MATCHSTATUS(self, e):
		# This appears to be a duplicate event of FULLTIME
		# So swallow this one to avoid double output
		if e.strMatchStatus == 'RESULT':
			return
		lstLine = []
		lstLine.append(('{status}: '.format(status=e.strMatchStatus), self.objOutput.C_BLUE))
		lstLine.append(('{homeTeam} {homeScore}'.format(homeTeam=e.strHomeTeam, homeScore=e.intHomeScore), self.objOutput.C_BLUE))
		lstLine.append(('-', self.objOutput.C_BLUE))
		lstLine.append(('{awayScore} {awayTeam}'.format(awayScore=e.intAwayScore, awayTeam=e.strAwayTeam), self.objOutput.C_BLUE))
		self.objOutput.addLine(lstLine)

	def _output_GOAL(self, e, bolPenalty=False):
		strPen        = '(pen)' if bolPenalty else ''
		strHomeColour = self.objOutput.C_GREEN if e.bolHomeTeam else self.objOutput.C_END
		strAwayColour = self.objOutput.C_GREEN if not e.bolHomeTeam else self.objOutput.C_END

		lstLine = []
		lstLine.append(('GOAL: ', self.objOutput.C_GREEN))
		lstLine.append(('{homeTeam} {homeScore}'.format(homeTeam=e.strHomeTeam, homeScore=e.intHomeScore), strHomeColour))
		lstLine.append(('-', self.objOutput.C_END))
		lstLine.append(('{awayScore} {awayTeam} '.format(awayScore=e.intAwayScore, awayTeam=e.strAwayTeam), strAwayColour))
		lstLine.append(('{player}{pen} {mins}\''.format(player=e.strPlayer, pen=strPen, mins=e.intMins), self.objOutput.C_GREEN))
		self.objOutput.addLine(lstLine)

	def _output_PENALTY(self, e):
		strTeam = e.strHomeTeam if e.bolHomeTeam else e.strAwayTeam
		if e.strPenOutcome == 'SCORED':
			self._output_GOAL(e, True)

	# Main event loop
	# TODO: Tidy this up
	# TODO: Change sleeps to allow interrupts
	def run(self):
		bolFirstRun = True
		try:
			bolLastRunEmpty = False
			while not self.__objStop.isSet():
				lstEvents = self.objFeed.getEvents()

				if not lstEvents:
					if not bolLastRunEmpty:
						self.objOutput.addLine([('No matches in progress', self.objOutput.C_GREEN)])
					bolLastRunEmpty = True
					bolFirstRun     = False
					time.sleep(5)
					continue

				bolLastRunEmpty = False

				# The match events are an ordered list, newest first
				# Unless there is only one event (doh!) so put it in a list
				lstNewEvents = []
				if type(lstEvents) is not list:
					lstEvents = [lstEvents]

				# Find new events
				for dctEvent in lstEvents:
					objEvent = MatchEvent(dctEvent, self.objLogger)
					if  objEvent.strUniqueId != self.getLastEvent() \
					and (not bolFirstRun or (len(lstNewEvents) <= self.intFirstRunMaxEvents or self._bolReplay)):
						lstNewEvents.insert(0, objEvent)
					else:
						# Found an existing event so schtop!
						break

				if len(lstNewEvents) > 0:
					self.objLogger.info("Received {0} events".format(len(lstNewEvents)))
				# Loop through all new events (already ordered oldest first)
				for objEvent in lstNewEvents:
					if self.__objStop.isSet():
						break
					self.outputEvent(objEvent)

				if len(lstNewEvents) == 0 and not self.__objStop.isSet():
					time.sleep(5)
		except:
			self.objLogger.error(traceback.format_exc())
			self.stop()



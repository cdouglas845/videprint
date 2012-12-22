import time
import threading
import traceback

from models.events._match_event import MatchEvent
from models.events.goal import Goal
from models.events.dismissal import Dismissal
from models.events.status import Status

# Designed to run its own thread to allow multiple feeds
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

	def isStopped(self):
		return self.__objStop.isSet()

	def enableReplay(self):
		self._bolReplay = True

	def getLastEvent(self):
		return self._strLastEvent

	def pause(self, intSeconds):
		intPaused = 0
		while (not self.isStopped() and intPaused < intSeconds):
			time.sleep(1)
			intPaused += 1

	def loadEvent(self, dctEvent):
		# TODO: This needs decoupling!
		strEventType = dctEvent['event']['eventType']
		if strEventType == MatchEvent.ET_GOAL:
			return Goal(dctEvent)
		if strEventType == MatchEvent.ET_PENALTY:
			return Goal(dctEvent)
		if strEventType == MatchEvent.ET_MATCHSTATUS:
			return Status(dctEvent)
		if strEventType == MatchEvent.ET_DISMISSAL:
			return Dismissal(dctEvent)

	def outputEvent(self, objEvent):
		objEvent.writeOutput(self.objOutput)
		self._strLastEvent = objEvent.strUniqueId

	# Main event loop
	# TODO: Tidy this up
	def run(self):
		bolFirstRun = True
		try:
			bolLastRunEmpty = False
			while not self.isStopped():
				lstEvents = self.objFeed.getEvents()

				if not lstEvents:
					if not bolLastRunEmpty:
						self.objOutput.addLine([('No matches in progress', self.objOutput.C_GREEN)])
					bolLastRunEmpty = True
					bolFirstRun     = False
					self.pause(30)
					continue

				bolLastRunEmpty = False
				lstNewEvents    = []

				# Find new events
				for dctEvent in lstEvents:
					objEvent = self.loadEvent(dctEvent)
					if  objEvent.strUniqueId != self.getLastEvent() \
					and (not bolFirstRun or len(lstNewEvents) <= self.intFirstRunMaxEvents or self._bolReplay):
						lstNewEvents.insert(0, objEvent)
					else:
						# Found an existing event so schtop!
						break

				if len(lstNewEvents) > 0:
					self.objLogger.info("Received {0} events".format(len(lstNewEvents)))
				# Loop through all new events (already ordered oldest first)
				for objEvent in lstNewEvents:
					if self.isStopped():
						break
					self.outputEvent(objEvent)

				# To save spamming the feed too much
				if len(lstNewEvents) == 0:
					self.pause(10)
		except:
			self.objLogger.error(traceback.format_exc())
			self.stop()



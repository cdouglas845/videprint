# Abstract
class MatchEvent(object):

	ET_DISMISSAL   = 'DISMISSAL'
	ET_MATCHSTATUS = 'MATCHSTATUS'
	ET_GOAL        = 'GOAL'
	ET_PENALTY     = 'PENALTY'

	def __init__(self, jEvent):
		self.dctEvent      = jEvent['event']
		self.strEventId    = self.dctEvent['eventId']
		self.intMatchId    = jEvent['matchId']
		self.strUniqueId   = self.intMatchId + '_' + self.strEventId
		self.strEventType  = self.dctEvent['eventType']
		self.strEventCode  = self.dctEvent['eventCode']
		self.strHomeTeam   = jEvent['homeTeam']['name']
		self.strAwayTeam   = jEvent['awayTeam']['name']
		self.bolCorrection = self.dctEvent['correction']

	def writeOutput(self, objOutput):
		raise NotImplementedError('writeOutput() has not been implemented in this class')

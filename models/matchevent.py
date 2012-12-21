class MatchEvent:
	ET_DISMISSAL   = 'DISMISSAL'
	ET_MATCHSTATUS = 'MATCHSTATUS'
	ET_GOAL        = 'GOAL'
	ET_PENALTY     = 'PENALTY'

	def __init__(self, jEvent, objLogger):
		self.dctEvent      = jEvent['event']
		self.strEventId    = self.dctEvent['eventId']
		self.intMatchId    = jEvent['matchId']
		self.strUniqueId   = self.intMatchId + '_' + self.strEventId
		self.strEventType  = self.dctEvent['eventType']
		self.strEventCode  = self.dctEvent['eventCode']
		self.strHomeTeam   = jEvent['homeTeam']['name']
		self.strAwayTeam   = jEvent['awayTeam']['name']
		self.bolCorrection = self.dctEvent['correction']
		self.objLogger     = objLogger

		# Load extra details depending on the type of event
		fncLoader = getattr(self, '_load_' + self.strEventType, None)

		if callable(fncLoader):
			fncLoader()
		else:
			# Unknown eventType found, log the error
			objLogger.error('MatchEvent encountered an unknown event type: ' + self.strEventType)
			objLogger.error('Details: ' + repr(jEvent))

	def _load_DISMISSAL(self):
		self.intMins         = self.dctEvent['minutesIntoMatch']
		self.strPlayer       = self.dctEvent['player']['name']
		self.bolHomeTeam     = True if self.dctEvent['teamType'] == 'HOME' else False
		self.strComment      = self.dctEvent['comment']
		self.intMinsInInjury = self.dctEvent['minutesIntoInjuryTime'] if 'minutesIntoInjuryTime' in self.dctEvent else 0

	def _load_MATCHSTATUS(self):
		self.strMatchStatus  = self.dctEvent['matchStatus'] # FULLTIME/RESULT
		self.intHomeScore    = self.dctEvent['homeScore']
		self.intAwayScore    = self.dctEvent['awayScore']

	def _load_GOAL(self):
		self.intMins         = self.dctEvent['minutesIntoMatch']
		self.intHomeScore    = self.dctEvent['homeScore']
		self.intAwayScore    = self.dctEvent['awayScore']
		self.bolOwnGoal      = self.dctEvent['ownGoal']
		self.strPlayer       = self.dctEvent['player']['name']
		self.bolHomeTeam     = True if self.dctEvent['teamType'] == 'HOME' else False
		self.intMinsInInjury = self.dctEvent['minutesIntoInjuryTime'] if 'minutesIntoInjuryTime' in self.dctEvent else 0

	def _load_PENALTY(self):
		self._load_GOAL()
		self.strPenOutcome   = self.dctEvent['penaltyOutcome'] # MISSED/SCORED


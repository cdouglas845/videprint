from models.events._match_event import MatchEvent

class Status(MatchEvent):

	TEAM_TYPE_HOME = 'HOME'
	TEAM_TYPE_AWAY = 'AWAY'

	def __init__(self, jEvent):
		super(Status, self).__init__(jEvent)
		self.strMatchStatus  = self.dctEvent['matchStatus'] # FULLTIME/RESULT
		self.intHomeScore    = self.dctEvent['homeScore']
		self.intAwayScore    = self.dctEvent['awayScore']

	def getStatusOutput(self):
		return '{status}: '.format(status=self.strMatchStatus)

	def getHomeOutput(self):
		return '{homeTeam} {homeScore}'.format(homeTeam=self.strHomeTeam, homeScore=self.intHomeScore)

	def getAwayOutput(self):
		return '{awayScore} {awayTeam}'.format(awayScore=self.intAwayScore, awayTeam=self.strAwayTeam)

	def writeOutput(self, objOutput):
		# This appears to be a duplicate event of FULLTIME
		# So swallow this one to avoid double output
		if self.strMatchStatus == 'RESULT':
			return

		lstLine = []
		lstLine.append((self.getStatusOutput(), objOutput.C_BLUE))
		lstLine.append((self.getHomeOutput(), objOutput.C_BLUE))
		lstLine.append(('-', objOutput.C_BLUE))
		lstLine.append((self.getAwayOutput(), objOutput.C_BLUE))
		objOutput.addLine(lstLine)



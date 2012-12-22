from models.events._match_event import MatchEvent

class Goal(MatchEvent):

	TEAM_TYPE_HOME = 'HOME'
	TEAM_TYPE_AWAY = 'AWAY'

	def __init__(self, jEvent):
		super(Goal, self).__init__(jEvent) # Frank! Super Goals!
		self.intMins         = self.dctEvent['minutesIntoMatch']
		self.intHomeScore    = self.dctEvent['homeScore']
		self.intAwayScore    = self.dctEvent['awayScore']
		self.bolOwnGoal      = self.dctEvent['ownGoal']
		self.strPlayer       = self.dctEvent['player']['name']
		self.strTeamType     = self.dctEvent['teamType']

	def isHomeGoal(self):
		return self.strTeamType == self.TEAM_TYPE_HOME

	def isAwayGoal(self):
		return self.strTeamType == self.TEAM_TYPE_AWAY

	def getMinsInInjury(self):
		intMinsInInjury = 0
		if 'minutesIntoInjuryTime' in self.dctEvent:
			intMinsInInjury = self.dctEvent['minutesIntoInjuryTime']
		return intMinsInInjury

	def getHomeOutput(self):
		return '{homeTeam} {homeScore}'.format(homeTeam=self.strHomeTeam, homeScore=self.intHomeScore)

	def getAwayOutput(self):
		return '{awayScore} {awayTeam}'.format(awayScore=self.intAwayScore, awayTeam=self.strAwayTeam)

	def getScorerOutput(self):
		return '{player}{pen} {mins}\''.format(player=self.strPlayer, pen='', mins=self.intMins)

	def writeOutput(self, objOutput):
		strHomeColour = objOutput.C_GREEN if self.isHomeGoal() else objOutput.C_END
		strAwayColour = objOutput.C_GREEN if self.isAwayGoal() else objOutput.C_END
		lstLine       = []

		lstLine.append(('GOAL: ', objOutput.C_GREEN))
		lstLine.append((self.getHomeOutput(), strHomeColour))
		lstLine.append(('-', objOutput.C_END))
		lstLine.append((self.getAwayOutput(), strAwayColour))
		lstLine.append((' ', objOutput.C_END))
		lstLine.append((self.getScorerOutput(), objOutput.C_GREEN))
		objOutput.addLine(lstLine)


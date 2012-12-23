from models.events._match_event import MatchEvent

class Dismissal(MatchEvent):

	TEAM_TYPE_HOME = 'HOME'
	TEAM_TYPE_AWAY = 'AWAY'

	def __init__(self, jEvent):
		super(Dismissal, self).__init__(jEvent)
		self.intMins         = self.dctEvent['minutesIntoMatch']
		self.strPlayer       = self.dctEvent['player']['name']
		self.strTeamType     = self.dctEvent['teamType']
		self.strComment      = self.dctEvent['comment']

	def isHomeDismissal(self):
		return self.strTeamType == self.TEAM_TYPE_HOME

	def isAwayDismissal(self):
		return self.strTeamType == self.TEAM_TYPE_AWAY

	def getMinsInInjury(self):
		intMinsInInjury = 0
		if 'minutesIntoInjuryTime' in self.dctEvent:
			intMinsInInjury = self.dctEvent['minutesIntoInjuryTime']
		return intMinsInInjury

	def getPlayerOutput(self):
		strTeam = self.strHomeTeam if self.isHomeDismissal else self.strAwayTeam
		return '{player} ({team}) '.format(player=self.strPlayer, team=strTeam)

	def getCommentOutput(self):
		return ' - {comment} {mins}\''.format(comment=self.strComment, mins=self.intMins)

	def writeOutput(self, objOutput):
		lstLine = []
		lstLine.append(('OFF: ', objOutput.C_RED))
		lstLine.append((self.getPlayerOutput(), objOutput.C_RED))
		lstLine.append((self.getCommentOutput(), objOutput.C_END))
		objOutput.addLine(lstLine)


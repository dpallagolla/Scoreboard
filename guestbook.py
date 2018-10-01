import os
import urllib
import uuid

from google.appengine.api import users
from google.appengine.ext import ndb

import jinja2
import webapp2

JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True)
# [END imports]

# [START DB]
class Team(ndb.Model):
    teamID = ndb.StringProperty(indexed=True)
    Player1 = ndb.StringProperty(indexed=True)
    Player2 = ndb.StringProperty(indexed=True)
    totalScore = ndb.IntegerProperty(indexed=True)


class Match(ndb.Model):
    matchID = ndb.StringProperty(indexed=False)
    team1 = ndb.StringProperty(indexed=True)
    team2 = ndb.StringProperty(indexed=True)
    team1Score = ndb.IntegerProperty(indexed=True)
    team2Score = ndb.IntegerProperty(indexed=True)
    location = ndb.StringProperty(indexed=True)
    winner = ndb.StringProperty(indexed=True)
    gametype = ndb.StringProperty(indexed=True)
# [END DB]


# [START main_page]
class MainPage(webapp2.RequestHandler):

    def get(self):

        query = Team.query().order(-Team.totalScore)
        query = query.fetch()
        print "Query:"+str(query)
        print "length:"+str(len(query))
        # assign indexes/ranks to the teams
        iRank = 1
        loopLength = len(query)-2
        i = 0
        teams = []
        for q in query:
            q.rank = lambda: None
            setattr(q,"rank",0)
        while i <= loopLength and iRank<=10:
            print "i:"+str(i)
            print "setting rank of team "+ str(query[i].teamID) + " as rank " + str(iRank)
            query[i].rank = lambda: None
            setattr(query[i],"rank",iRank)
            teams.append(query[i])
            if query[i].totalScore != query[i+1].totalScore:
                iRank = iRank+1
            i = i+1
        print "outside loop"
        queryLength = len(query)
        if query[queryLength-1].totalScore == query[queryLength-2].totalScore:
            print "setting rank of team "+ str(query[queryLength-1].teamID) + " as rank " + str(int(getattr(query[queryLength-2],"rank")))
            previousRank = getattr(query[queryLength-2],"rank")
            setattr(query[queryLength-1],"rank",int(previousRank,"rank"))
            teams.append(query[queryLength-1])
        else:
            print "setting rank of team "+ str(query[queryLength-1].teamID) + " as rank " + str(int(getattr(query[queryLength-2],"rank"))+1)
            previousRank = getattr(query[queryLength-2],"rank")
            if(previousRank!=10):
                setattr(query[queryLength-1],"rank",int(getattr(query[queryLength-2],"rank"))+1)
                teams.append(query[queryLength-1])

        # assign indexes/ranks to the teams
        template_values = {
          'createTeamUrl': '/createTeam',
          'recordMatchScoresUrl': '/recordMatchScores',
          'teams': teams

        }

        template = JINJA_ENVIRONMENT.get_template('index.html')
        self.response.write(template.render(template_values))
# [END main_page]

class createTeam(webapp2.RequestHandler):

    def get(self):
       
        template_values = {
        'createTeamUrl': '/createTeam',
        'recordMatchScoresUrl': '/recordMatchScores'        
        }

        template = JINJA_ENVIRONMENT.get_template('createTeam.html')
        self.response.write(template.render(template_values))
    
    def post(self):
        teamName = self.request.get('teamName')
        splayer1 = self.request.get('player1')
        splayer2 = self.request.get('player2')
        query = Team.query(Team.teamID==teamName)
        query = query.fetch()
        query1 = Team.query(Team.Player1==splayer1,Team.Player2==splayer2)
        query1 = query1.fetch()
        teamName = str(teamName)
        splayer1 = str(splayer1)
        splayer2 = str(splayer2)
        if teamName == "" or splayer1 == "" or splayer2 == "":
            template_values = {
            'createTeamUrl': '/createTeam',
            'recordMatchScoresUrl': '/recordMatchScores',
            'Header': 'Error!',
            'Message': 'All fields are mandatory for team creation!',
            'alertClass': 'alert-danger'      
            }
            template = JINJA_ENVIRONMENT.get_template('infoPage.html')
            self.response.write(template.render(template_values))
        elif query:
            template_values = {
            'createTeamUrl': '/createTeam',
            'recordMatchScoresUrl': '/recordMatchScores',
            'Header': 'Error!',
            'Message': 'Team Name alreay taken!',
            'alertClass': 'alert-danger'      
            }
            template = JINJA_ENVIRONMENT.get_template('infoPage.html')
            self.response.write(template.render(template_values))
            #The team name is already taken
        elif query1:
            template_values = {
            'createTeamUrl': '/createTeam',
            'recordMatchScoresUrl': '/recordMatchScores',
            'Header': 'Error!',
            'Message': 'Both players are already part of another team!',
            'alertClass': 'alert-danger'
            }
            template = JINJA_ENVIRONMENT.get_template('infoPage.html')
            self.response.write(template.render(template_values))
            #both players are already part of a team
        else:
            team = Team(teamID = teamName,
                    Player1 = splayer1,
                    Player2 = splayer2,
                    totalScore = 0
                    )
            team.put()
            template_values = {
            'createTeamUrl': '/createTeam',
            'recordMatchScoresUrl': '/recordMatchScores',
            'Header': 'Success!',
            'Message': 'Team has been created',
            'alertClass': 'alert-success'
            }
            template = JINJA_ENVIRONMENT.get_template('infoPage.html')
            self.response.write(template.render(template_values))


class recordMatchScores(webapp2.RequestHandler):

    def get(self):
        query = Team.query()
        teams = query.fetch()
        template_values = {
        'createTeamUrl': '/createTeam',
        'recordMatchScoresUrl': '/recordMatchScores',
        'teams': teams
        }

        template = JINJA_ENVIRONMENT.get_template('recordMatchScores.html')
        self.response.write(template.render(template_values))

    def post(self):
        # matchid,team1name,team2name,team1score,team2score,location,winner,gametype
        team1name = self.request.get('team1name')
        team2name = self.request.get('team2name')
        team1score = self.request.get('team1score')
        team2score = self.request.get('team2score')
        location = self.request.get('location')
        gametype = self.request.get('gametype')

        print str(team1name)+" "+str(team2name)

        if team1name == team2name:
            template_values = {
            'createTeamUrl': '/createTeam',
            'recordMatchScoresUrl': '/recordMatchScores',
            'Header': 'Error!',
            'Message': 'A team cannot play against itself!',
            'alertClass': 'alert-danger'
            }
            template = JINJA_ENVIRONMENT.get_template('infoPage.html')
            self.response.write(template.render(template_values))
        elif team1score=="" or team2score=="":
            template_values = {
            'createTeamUrl': '/createTeam',
            'recordMatchScoresUrl': '/recordMatchScores',
            'Header': 'Error!',
            'Message': 'Scores cannot be empty!',
            'alertClass': 'alert-danger'
            }
            template = JINJA_ENVIRONMENT.get_template('infoPage.html')
            self.response.write(template.render(template_values))
        else:
            team1score = int(team1score)
            team2score = int(team2score)
            winner = ""
            if team1score>team2score:
                winner = team1name
            elif team2score>team1score:
                winner = team2name
            matchid = str(uuid.uuid1())
            match = Match( matchID = matchid,
                           team1 = team1name,
                           team2 = team2name,
                           team1Score = team1score,
                           team2Score = team2score,
                           location = location,
                           winner = winner,
                           gametype = gametype
            )
            match.put()
            team1 = Team.query(Team.teamID == team1name)
            team1 = team1.fetch()
            team1 = team1[0]
            team1oldscore = int(team1.totalScore)
            team1.totalScore = team1oldscore + (team1score-team2score)
            team1.put()
            team2 = Team.query(Team.teamID == team2name)
            team2 = team2.fetch()
            team2 = team2[0]
            team2oldscore = int(team2.totalScore)
            team2.totalScore = team2oldscore + (team2score-team1score)
            team2.put()
            template_values = {
            'createTeamUrl': '/createTeam',
            'recordMatchScoresUrl': '/recordMatchScores',
            'Header': 'Success!',
            'Message': 'Scores updated successfully!',
            'alertClass': 'alert-success'
            }
            template = JINJA_ENVIRONMENT.get_template('infoPage.html')
            self.response.write(template.render(template_values))
            

class teamDetail(webapp2.RequestHandler):
    def get(self):
        teamname = self.request.get('teamname')
        matchesQuery = Match.query(ndb.OR(Match.team1 == teamname,Match.team2 == teamname ))
        matches = matchesQuery.fetch()
        template_values = {
        'createTeamUrl': '/createTeam',
        'recordMatchScoresUrl': '/recordMatchScores',
        'matches': matches
        }
        print matches
        template = JINJA_ENVIRONMENT.get_template('teamDetail.html')
        self.response.write(template.render(template_values))

# [START app]
app = webapp2.WSGIApplication([
    ('/', MainPage),
    ('/home',MainPage),
    ('/createTeam', createTeam),
    ('/recordMatchScores', recordMatchScores),
    ('/teamDetail',teamDetail),
], debug=True)
# [END app]

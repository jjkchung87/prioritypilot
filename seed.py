from models import db, Golfer, Tournament, TournamentGolfer
from app import app
import requests

db.drop_all()
db.create_all()


#******************************************************************************************************************************************************************************
#API Requests

BASE_URL = 'https://feeds.datagolf.com'
FILE_FORMAT= 'json'
API_KEY = '53f0ef0e0b15d5adc6a304967568'

#******************************************************************************************************************************************************************************
#GET GOLFERS

res_golfers = requests.get(f"{BASE_URL}/get-player-list",params={"file_format": FILE_FORMAT,
                                                             "key": API_KEY})

golfers = [{'name':golfer['player_name'].split(", "), 'dg_id':golfer['dg_id']} for golfer in res_golfers.json()]

for golfer in golfers:
    full_name = golfer['name']
    golfer['last_name'] = full_name[0]
    golfer['first_name'] = ' '.join(full_name[1:]) if len(full_name) > 1 else ''
    del golfer['name']

for golfer in golfers:
    g = Golfer(first_name=golfer['first_name'], last_name=golfer['last_name'], dg_id=golfer['dg_id'])
    db.session.add(g)
    db.session.commit()

#******************************************************************************************************************************************************************************
#GET TOURNAMENTS


res_tournaments = requests.get(f"{BASE_URL}/historical-raw-data/event-list", params={"file_format":FILE_FORMAT,
                                                                                     "key":API_KEY})


tournaments = [{"dg_id":tournament["event_id"], "tournament_name":tournament["event_name"], "calendar_year":tournament["calendar_year"], "date":tournament["date"], "tour": tournament["tour"]} for tournament in res_tournaments.json()]

for tournament in tournaments:
    t = Tournament(tournament_name=tournament["tournament_name"],
                   calendar_year=tournament["calendar_year"],
                   date=tournament["date"],
                   tour=tournament["tour"],
                   dg_id=tournament["dg_id"])
    
    db.session.add(t)
    db.session.commit()

#******************************************************************************************************************************************************************************
#GET TOURNAMENT RESULTS



res_tournament_results = requests.get(f"{BASE_URL}/historical-raw-data/rounds",params={"tour":"pga",
                                                                    "event_id":"all",
                                                                    "year": 2023,
                                                                    "file_format": FILE_FORMAT,
                                                                    "key": API_KEY})

tournament_results = res_tournament_results.json()


for key, value in tournament_results.items():
    tournament_name = value["event_name"]
    calendar_year = value["year"]
    date = value["event_completed"]
    dg_id = value["event_id"]
    
    
    t = Tournament.query.filter(Tournament.tournament_name==tournament_name, Tournament.calendar_year==calendar_year, Tournament.dg_id==dg_id).first()

    if not t:
        t = Tournament(tournament_name = tournament_name, calendar_year=calendar_year, dg_id=dg_id, date=date)
        db.session.add(t)
        db.session.commit()

    for player in value['scores']:
        
        g = Golfer.query.filter_by(dg_id=player['dg_id']).first()

        if not g:
            full_name = player['player_name'].split(", ")
            last_name= full_name[0]
            first_name = ' '.join(full_name[1:]) if len(full_name) > 1 else ''
            g = Golfer(dg_id = player['dg_id'], first_name=first_name, last_name=last_name)
            db.session.add(g)
            db.session.commit()
                    
        for key, value in player.items():
            if 'round' in key:
                round = int(key.split("_")[1])
                score = value["score"]
                tg = TournamentGolfer(tournament_id = t.id,
                                      golfer_id = g.id,
                                      tournament_name = t.tournament_name, 
                                      calendar_year = t.calendar_year,
                                      golfer_dg_id = g.dg_id,
                                      tournament_dg_id = t.dg_id,
                                      round = round, 
                                      golfer_score=score )
                db.session.add(tg)
                db.session.commit()



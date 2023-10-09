from Archives.models import db, Golfer, Tournament, TournamentGolfer, User, League, Team
from app import app
import requests
from Archives.golfers_images import golfer_images


# db.session.query(Golfer).delete()
# db.session.query(Tournament).delete()
# db.session.commit()

db.session.rollback()
db.drop_all()
db.create_all()

DEFAULT_GOLFER_URL = "https://png.pngtree.com/png-clipart/20210915/ourmid/pngtree-user-avatar-placeholder-black-png-image_3918427.jpg"

#******************************************************************************************************************************************************************************
#API Requests

BASE_URL = 'https://feeds.datagolf.com'
FILE_FORMAT= 'json'
API_KEY = '53f0ef0e0b15d5adc6a304967568'

#******************************************************************************************************************************************************************************
#GET GOLFERS

# res_golfers = requests.get(f"{BASE_URL}/get-dg-rankings",params={"file_format": FILE_FORMAT,
#                                                              "key": API_KEY})

res_golfers = requests.get('https://feeds.datagolf.com/preds/get-dg-rankings?file_format=json&key=53f0ef0e0b15d5adc6a304967568')


# golfers = [{'name':golfer['player_name'].split(", "), 'dg_id':golfer['dg_id']} for golfer in res_golfers.json()]

golfers = [{'name':golfer['player_name'].split(", "), 'dg_id':golfer['dg_id'], 'owgr':golfer['owgr_rank']} for golfer in res_golfers.json()['rankings'] if golfer['owgr_rank'] != ""]


for golfer in golfers:
    full_name = golfer['name']
    golfer['last_name'] = full_name[0]
    golfer['first_name'] = ' '.join(full_name[1:]) if len(full_name) > 1 else ''
    golfer['golfer_image_URL'] = DEFAULT_GOLFER_URL  # Initialize with default URL
    golfer['joint_full_name'] = golfer['first_name']+' '+golfer['last_name']
    for gi in golfer_images:
        if gi['displayName'] == golfer['joint_full_name']:
            golfer['golfer_image_URL'] = gi['headshot']
            break
    g = Golfer(first_name=golfer['first_name'], last_name=golfer['last_name'], dg_id=golfer['dg_id'], golfer_image_url = golfer['golfer_image_URL'], owgr = int(golfer['owgr']))
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
                course_par = value["course_par"]
                if value["score"]:
                    score_vs_par = score - course_par
                else: 
                    score_vs_par = None
                tg = TournamentGolfer(tournament_id = t.id,
                                      golfer_id = g.id,
                                      tournament_name = t.tournament_name, 
                                      calendar_year = t.calendar_year,
                                      golfer_dg_id = g.dg_id,
                                      tournament_dg_id = t.dg_id,
                                      round = round,
                                      course_par = course_par, 
                                      score_vs_par = score_vs_par,
                                      golfer_score=score )
                db.session.add(tg)
                db.session.commit()

golfers_list = Golfer.query.all()

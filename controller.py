from models import db, connect_db, User, League, Team, Golfer, Tournament, TeamGolfer, TournamentGolfer, UserLeague, LeagueGolfer
from sqlalchemy import func, and_, case


#This file contains all controller functions that should be compartmentalized from view functions


def get_latest_tournament():
    """Get latest tournament available in database"""
  # Get the maximum tournament date from the query result
    max_tournament_date_result = db.session.query(func.max(Tournament.date)).first()
    max_tournament_date = max_tournament_date_result[0]  # Extract the datetime value

    # Format the datetime as a string
    # formatted_datetime = max_tournament_date.strftime("%Y-%m-%d %H:%M:%S")

    latest_tournament_id_subquery = (
        db.session.query(Tournament.id)
        .filter(Tournament.date == max_tournament_date)
        .filter(Tournament.tour == "pga")
    ).scalar()  # Use .scalar() to get the single value instead of a tuple

    #Query for latest tournament based on tournament in db with latest date
    return Tournament.query.get_or_404(latest_tournament_id_subquery)

    


def get_latest_tournament_results(tournament):
    """Gets results from latest tournament"""

    #Query for latest tournament's results
    return (
        db.session.query(
            Golfer.id.label("golfer_id"),
            func.concat(Golfer.first_name, ' ', Golfer.last_name).label("full_name"),
            Golfer.golfer_image_url.label("golfer_image_url"),
            func.sum(TournamentGolfer.score_vs_par).label("total_score_vs_par")
        )
        .join(Tournament, and_(
            Tournament.id == TournamentGolfer.tournament_id,
            Tournament.tournament_name == TournamentGolfer.tournament_name,
            Tournament.calendar_year == TournamentGolfer.calendar_year,
            Tournament.dg_id == TournamentGolfer.tournament_dg_id
        ))
        .filter(Tournament.id == tournament.id)
        .join(Golfer, Golfer.id == TournamentGolfer.golfer_id)  # Specify the join condition here
        .group_by(Golfer.id,"full_name",Golfer.golfer_image_url)
        .order_by("total_score_vs_par")
    ).all()



def get_league_results(league):
    """get results of a league"""

    return (
        db.session.query(
            Team.team_name,
            Team.id,
            func.sum(TournamentGolfer.score_vs_par).label("total_score_vs_par")
        )
        .join(Tournament, and_(
            Tournament.id == TournamentGolfer.tournament_id,
            Tournament.tournament_name == TournamentGolfer.tournament_name,
            Tournament.calendar_year == TournamentGolfer.calendar_year,
            Tournament.dg_id == TournamentGolfer.tournament_dg_id
        ))
        .filter(Tournament.date >= league.start_date, Tournament.date <= league.end_date)
        .join(Golfer, Golfer.id == TournamentGolfer.golfer_id)
        .join(TeamGolfer, TeamGolfer.golfer_id == Golfer.id)
        .join(Team,Team.id == TeamGolfer.team_id)
        .filter(Team.league_id == league.id)
        .group_by(Team.team_name, Team.id)
        .order_by("total_score_vs_par")
    ).all()


def get_top_golfers_in_league(league):
    """Get top golfers' results in given league"""

    return (db.session.query(
            func.concat(Golfer.first_name," ", Golfer.last_name).label("full_name"),
            Golfer.golfer_image_url.label("golfer_image_url"),
            Team.team_name,
            func.sum(TournamentGolfer.score_vs_par).label("total_score_vs_par")
        )
        .join(Tournament, and_(
        Tournament.id == TournamentGolfer.tournament_id,
        Tournament.tournament_name == TournamentGolfer.tournament_name,
        Tournament.calendar_year == TournamentGolfer.calendar_year,
        Tournament.dg_id == TournamentGolfer.tournament_dg_id
        ))
        .filter(Tournament.date >= league.start_date, Tournament.date <= league.end_date)
        .join(Golfer, Golfer.id == TournamentGolfer.golfer_id)
        .join(TeamGolfer, TeamGolfer.golfer_id == Golfer.id)
        .join(Team, Team.id == TeamGolfer.team_id)
        .filter(Team.league_id == league.id)
        .group_by("full_name", "golfer_image_url",Team.team_name)
        .order_by("total_score_vs_par")
    ).all()


def get_team_results(league, team):
    """get specified teams' results"""

    return (
        db.session.query(
            func.concat(Golfer.first_name," ", Golfer.last_name).label("full_name"),
            func.sum(TournamentGolfer.score_vs_par).label("total_score_vs_par")
        )
        .join(Tournament, and_(
            Tournament.id == TournamentGolfer.tournament_id,
            Tournament.tournament_name == TournamentGolfer.tournament_name,
            Tournament.calendar_year == TournamentGolfer.calendar_year,
            Tournament.dg_id == TournamentGolfer.tournament_dg_id
        ))
        .filter(Tournament.date >= league.start_date, Tournament.date <= league.end_date)
        .join(Golfer, Golfer.id == TournamentGolfer.golfer_id)
        .join(TeamGolfer, TeamGolfer.golfer_id == Golfer.id)
        .filter(TeamGolfer.team_id == team.id)
        .group_by("full_name")
    ).all()
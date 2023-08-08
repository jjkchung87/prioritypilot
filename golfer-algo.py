from sqlalchemy import func, and_, text

# *********************************************************************************************************************
# RECENT GOLFER SCORES

   # Calculate the date ranges for the last 30 days and prior 30 days
    last_30_days_end = datetime.utcnow()
    last_30_days_start = last_30_days_end - timedelta(days=30)
    prior_30_days_end = last_30_days_start - timedelta(days=1)
    prior_30_days_start = prior_30_days_end - timedelta(days=30)

    # Subquery to get the average score versus par for the last 30 days
    subquery_last_30_days = (db.session.query(TournamentGolfer.golfer_id,
                                            func.avg(TournamentGolfer.score_vs_par).label('avg_score_vs_par_last_30_days'))
                            .join(Tournament, and_(TournamentGolfer.tournament_name == Tournament.tournament_name,
                                                    TournamentGolfer.calendar_year == Tournament.calendar_year,
                                                    TournamentGolfer.tournament_dg_id == Tournament.dg_id))
                            .filter(and_(Tournament.date >= last_30_days_start,
                                        Tournament.date <= last_30_days_end))
                            .group_by(TournamentGolfer.golfer_id)
                            .subquery())

    # Subquery to get the average score versus par for the prior 30 days
    subquery_prior_30_days = (db.session.query(TournamentGolfer.golfer_id,
                                            func.avg(TournamentGolfer.score_vs_par).label('avg_score_vs_par_prior_30_days'))
                            .filter(and_(Tournament.date >= prior_30_days_start,
                                        Tournament.date <= prior_30_days_end))
                            .group_by(TournamentGolfer.golfer_id)
                            .subquery())

    # Main query to get the final table
    query = (db.session.query(subquery_last_30_days.c.golfer_id,
                            subquery_last_30_days.c.avg_score_vs_par_last_30_days,
                            subquery_prior_30_days.c.avg_score_vs_par_prior_30_days)
            .join(subquery_prior_30_days, subquery_last_30_days.c.golfer_id == subquery_prior_30_days.c.golfer_id)
            .order_by(subquery_last_30_days.c.avg_score_vs_par_last_30_days.asc())
            .all())

    # Output the results

    results = []
    for golfer_id, avg_score_vs_par_last_30_days, avg_score_vs_par_prior_30_days in query:
        golfer = Golfer.query.get(golfer_id)
        results.append({"id":golfer.id,
                        "first_name":golfer.first_name,
                        "last_name":golfer.last_name,
                        "avg_score_vs_par_last_30": int(avg_score_vs_par_last_30_days),
                        "avg_score_vs_par_prior_30": int(avg_score_vs_par_prior_30_days)})


# *********************************************************************************************************************
# LATEST TOURNAMENT SCORES


# Get the maximum tournament date from the query result
max_tournament_date_result = db.session.query(func.max(Tournament.date)).first()
max_tournament_date = max_tournament_date_result[0]  # Extract the datetime value

# Format the datetime as a string
formatted_datetime = max_tournament_date.strftime("%Y-%m-%d %H:%M:%S")

latest_tournament_id_subquery = (
    db.session.query(Tournament.id)
    .filter(Tournament.date == max_tournament_date)
    .filter(Tournament.tour == "pga")
).scalar()  # Use .scalar() to get the single value instead of a tuple

latest_tournament_results = (
    db.session.query(
        func.concat(Golfer.first_name, ' ', Golfer.last_name).label("full_name"),
        func.sum(TournamentGolfer.score_vs_par).label("total_score_vs_par")
    )
    .join(Tournament, and_(
        Tournament.id == TournamentGolfer.tournament_id,
        Tournament.tournament_name == TournamentGolfer.tournament_name,
        Tournament.calendar_year == TournamentGolfer.calendar_year,
        Tournament.dg_id == TournamentGolfer.tournament_dg_id
    ))
    .filter(Tournament.date == max_tournament_date)
    .filter(Tournament.tour == "pga")
    .join(Golfer, Golfer.id == TournamentGolfer.golfer_id)  # Specify the join condition here
    .group_by("full_name")
    .order_by("total_score_vs_par")
).all()

# 'SELECT concat(golfers.first_name, %(concat_1)s, golfers.last_name) AS full_name, sum(tournament_golfers.score_vs_par) AS total_score_vs_par \n
# FROM tournament_golfers 
# JOIN tournaments 
#   ON tournaments.id = tournament_golfers.tournament_id 
#       AND tournaments.tournament_name = tournament_golfers.tournament_name 
#       AND tournaments.calendar_year = tournament_golfers.calendar_year 
#       AND tournaments.dg_id = tournament_golfers.tournament_dg_id 
# JOIN golfers 
#   ON golfers.id = tournament_golfers.golfer_id \n
# WHERE tournaments.date = %(date_1)s 
#   AND tournaments.tour = %(tour_1)s 
# GROUP BY full_name 
# ORDER BY total_score_vs_par'



# *********************************************************************************************************************
# LEAGUE RESULTS


query = (
    db.session.query(
        Team.team_name,
        func.sum(TournamentGolfer.score_vs_par).label("total_score_vs_par")
    )
    .join(Tournament, and_(
        Tournament.id == TournamentGolfer.tournament_id,
        Tournament.tournament_name == TournamentGolfer.tournament_name,
        Tournament.calendar_year == TournamentGolfer.calendar_year,
        Tournament.dg_id == TournamentGolfer.tournament_dg_id
    ))
    .filter(Tournament.date >= '2023-01-01 00:00:00', Tournament.date <= '2023-08-31 00:00:00')
    .join(Golfer, Golfer.id == TournamentGolfer.golfer_id)
    .join(TeamGolfer, TeamGolfer.golfer_id == Golfer.id)
    .join(Team,Team.id == TeamGolfer.team_id)
    .filter(Team.league_id == 2)
    .group_by(Team.team_name)
).all()

# *********************************************************************************************************************
# TEAM RESULTS

query = (
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

# *********************************************************************************************************************
# TOP GOLFERS IN LEAGUE

top_golfers_in_league = (
    db.session.query(
        func.concat(Golfer.first_name," ", Golfer.last_name).label("full_name"),
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
    .group_by("full_name", Team.team_name)
    .order_by("total_score_vs_par")
).all()

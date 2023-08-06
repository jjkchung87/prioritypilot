from sqlalchemy import func, and_, text

# Calculate the dates for the last 30 days and the prior 30 days

last_30_days_end = func.current_date()
last_30_days_start = last_30_days_end - 30
prior_30_days_end = last_30_days_start - 1
prior_30_days_start = prior_30_days_end - 30


# Subquery to get the average score versus par for the last 30 days
subquery_last_30_days = (db.session.query(TournamentGolfer.golfer_id,
                                          func.avg(TournamentGolfer.score_vs_par).label('avg_score_vs_par_last_30_days'))
                         .filter(and_(TournamentGolfer.golfer_id == Tournament.golfer_id,
                                      Tournament.date >= last_30_days_start,
                                      Tournament.date <= last_30_days_end))
                         .group_by(TournamentGolfer.golfer_id)
                         .subquery())

# Subquery to get the average score versus par for the prior 30 days
subquery_prior_30_days = (db.session.query(TournamentGolfer.golfer_id,
                                           func.avg(TournamentGolfer.score_vs_par).label('avg_score_vs_par_prior_30_days'))
                          .filter(and_(TournamentGolfer.golfer_id == Tournament.golfer_id,
                                       Tournament.date >= prior_30_days_start,
                                       Tournament.date <= prior_30_days_end))
                          .group_by(TournamentGolfer.golfer_id)
                          .subquery())

# Main query to get the final table
query = (db.session.query(TournamentGolfer.golfer_id,
                          func.avg(TournamentGolfer.score_vs_par).label('avg_score_vs_par_last_30_days'),
                          subquery_prior_30_days.c.avg_score_vs_par_prior_30_days)
         .filter(TournamentGolfer.golfer_id == subquery_last_30_days.c.golfer_id)
         .group_by(TournamentGolfer.golfer_id)
         .order_by(func.avg(TournamentGolfer.score_vs_par).asc())
         .all())

# Output the results

results = []
for golfer_id, avg_score_vs_par_last_30_days, avg_score_vs_par_prior_30_days in query:
    golfer = Golfer.query.get(golfer_id)
    results.append({"id":golfer.id,
                    "first_name":golfer.first_name,
                    "last_name":golfer.last_name,
                    "avg_score_vs_par_last_30": avg_score_vs_par_last_30_days,
                    "avg_score_vs_par_prior_30":avg_score_vs_par_prior_30_days})

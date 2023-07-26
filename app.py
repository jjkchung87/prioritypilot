import os

from flask import Flask, render_template, request, flash, redirect, session, g, jsonify
from flask_debugtoolbar import DebugToolbarExtension
from sqlalchemy.exc import IntegrityError
import requests


from models import db, connect_db, User, League, Team, Golfer, Tournament, UserGolfer, LeagueTeam, TeamGolfer, TournamentGolfer


app = Flask(__name__)

# Get DB_URI from environ variable (useful for production/testing) or,
# if not set there, use development local db.
app.config['SQLALCHEMY_DATABASE_URI'] = (
    os.environ.get('DATABASE_URL', 'postgresql:///golf_fantasy'))

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['EXPLAIN_TEMPLATE_LOADING'] = True
app.config['SQLALCHEMY_ECHO'] = False
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', "it's a secret")
app.debug=True
toolbar = DebugToolbarExtension(app)
app.app_context().push()
connect_db(app)




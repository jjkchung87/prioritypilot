# Golfantasy #
LINK TO SITE HERE

_Golf fantasy app where users can create/join leagues, create teams comprised of professional golfers, and compete against other users._

## Features ##

- Users can join existing leagues or create their own, choosing between public or private access.
- Users build their teams consisting of PGA Tour players, in a live, real-time draft, leveraging Websockets
- Teams compete against each other and the team with the lowest score at the end of the league season is the winner
- Scores are based on the real-life performance of the golfers on their team, which are updated daily

## Future Features ##

- Users can "Friend" and follow other users
- Live chat with other users
- Golf-related news and updates
- Addition other golf stats (e.g. Driving distance, Greens in Regulation) for more robust gameplay
- Mobile-friendly interface

## User Flow ##

1) First time visitors will be directed to create a new account to join
2) After joining, the user can either create or join a league. If the user creates a new league, they are the league manager and can set league settings
3) When the draft begins, users will take turns drafting golfers to their team. The draft is live and users will see which golfers each team is drafting
4) Once draft is complete, the league season is in play. Team scores will update daily based on real life performance of the golfers on their team. Users can view team and golfer scores in the league dash.
5) Once season is over, a winner is crowned!


## API ##

- Golfantasy leverages golfer data from [Data-golf API](https://datagolf.com/api-access)

## Tech Stack ##

### Front-end Stack ###

_HTML, CSS, Bootstrap, DataTables_

### Back-end Stack ###

_Python, Flask, Flask-SocketIO, SQLAlchemy, Flask-WTForms_



## Appendices ##

- [Proposal](https://docs.google.com/document/d/1nWq9YlgI9vl2aBwWGQV3Mdgf-41waVLSlCzAkwAsZnM/edit)


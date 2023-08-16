// FILE PURPOSE ********************************************************************************************************
//Class models to generate instances of currently logged in user, and their respective team and leagues they are viewing/modifying.
//Async requests are made to Golfantasy API to retrieve current user, league, and team data

const BASE_URL = "/golfantasy/api"

class User {
    constructor({
        id,
        username,
        teams=[],
        leagues=[],

    }){
        this.id = id,
        this.username = username,
        this.teams = teams.map(t => new Team(t)),
        this.leagues= leagues.map(l => new League(l))
    }

    static async signUp(formData){
        const res = await axios.post(`/golfantasy/signup`,formData)

        const user = new User({id:res.data['user']['id'],
                        username:res.data['user']['username'],
                        teams : res.data['user']['teams'],
                        leagues : res.data['user']['leagues']})

        return {
            "success":res.data.success,
            "user": user
        }
    }

    static async authenticate(username, password){
        const data = {username, password}
        const res = await axios.post(`${BASE_URL}/users/authenticate`, data)
        const {user} = res.data

        return new User({id:user.id,
            username:user.username,
            teams : user.teams,
            leagues : user.leagues})

    }

    static async retrieveCurrentUser(id){
        const res = await axios.get(`${BASE_URL}/users/${id}`)
        const {user} = res.data

        return new User({id:user.id,
            username:user.username,
            teams : user.teams,
            leagues : user.teams})
    }
    

}

class League {
    constructor({
        id,
        league_name,
        start_date,
        end_date,
        privacy,
        golfer_count,
        max_teams,
        draft_completed,
        draft_pick_index,
        draft_pick_count,
        teams=[],
        golfers=[],
        draft_order
    }){
        this.id = id,
        this.league_name = league_name,
        this.start_date = start_date,
        this.end_date = end_date,
        this.privacy = privacy,
        this.golfer_count = golfer_count,
        this.max_teams = max_teams,
        this.draft_completed = draft_completed,
        this.draft_pick_index = draft_pick_index,
        this.draft_pick_count = draft_pick_count,
        this.teams = teams.map(t => new Team(t))
        this.golfers = golfers.map(g => new Golfer(g))
        this.draft_order = draft_order
    }

    static async getLeague(league_id){
        const res = await axios.get(`${BASE_URL}/leagues/${league_id}`)
        const league = res.data
        return new League({
            id:league.id,
            league_name:league.league_name,
            start_date: league.start_date,
            end_date: league.end_date,
            privacy: league.privacy,
            golfer_count: league.golfer_count,
            max_teams: league.max_teams,
            draft_completed: league.draft_completed,
            draft_pick_index: league.draft_pick_index,
            draft_pick_count: league.draft_pick_count,
            teams: league.teams,
            golfers: league.golfers,
            draft_order: league.draft_order
        })
    }


}


class Team {
    constructor({
        id,
        team_name,
        user_id,
        league_id,
        golfers=[]
        }){
        this.id = id,
        this.team_name = team_name,
        this.user_id =user_id,
        this.league_id = league_id,
        this.golfers = golfers.map(g => new Golfer(g))
    }

    static async getTeam(teamId){
        const res = await axios.get(`${BASE_URL}/teams/${teamId}`)
        return new Team(res.data.team)
    }

    async addOrRemoveFromQueue(golferId){
        let clickedGolfer = golferList.find(g => {g.id == golferId})
        
        for(let golfer of this.queue){
            if(golfer==clickedGolfer){
                this.queue = this.queue.filter(g => golfer !== clickedGolfer)
            } else {
                this.queue.push(clickedGolfer)
            }
        }
    }
}

// class TeamList {
//     constructor(teams) {
//         this.teams = teams;
//     }

//     static async getTeamsInLeague(leagueId) {
//         const res = await axios.get(`${BASE_URL}/leagues/${leagueId}/teams`);
//         console.log(res)
//         const teams = res.data.teams.map(t => {
//             const golfers = t.golfers.map(g => {
//                 return new Golfer({
//                     id: g.id,
//                     first_name: g.first_name,
//                     last_name: g.last_name
//                 });
//             });
//             return new Team({
//                 id: t.id,
//                 team_name: t.team_name,
//                 user_id: t.user_id,
//                 league_id: t.league_id,
//                 created_at: t.created_at,
//                 golfers: golfers
//             });
//         });

//         return new TeamList(teams);
//     }
// }



class Golfer {
    constructor({
        id,
        first_name,
        last_name,
        owgr
    }){
        this.id = id,
        this.first_name = first_name,
        this.last_name = last_name,
        this.owgr = owgr
    }

    static async getGolfer(golferId){
        const res = await axios.get(`${BASE_URL}/golfers/${golferId}`)
        const {golfer} = res.data
        return new Golfer({
            id:golfer.id,
            first_name: golfer.first_name,
            last_name: golfer.last_name,
            owgr: golfer.owgr
        })
    }
}

class GolferList{
    constructor(golfers){
        this.golfers = golfers
    }

    static async getAllGolfers(){
        const res = await axios.get(`${BASE_URL}/golfers`)
        const golfers = res.data.golfers.map(g => {
            const {golfer} = g
            return new Golfer({
                id:golfer.id,
                first_name: golfer.first_name,
                last_name: golfer.last_name,
                owgr: golfer.owgr
            })
        })
        return new GolferList(golfers)
    }

    static async getAvailableGolfers(league_id){
        const res = await axios.get(`${BASE_URL}/leagues/${league_id}/golfers/available`)
        console.log(res)
        const golfers = res.data.golfers.map(g => {
            return new Golfer({
                id:golfer.id,
                first_name: golfer.first_name,
                last_name: golfer.last_name,
                owgr: golfer.owgr
            })
        })
        return new GolferList(golfers)
    }

}

class Tournament {
    constructor({
        id,
        tournament_name,
        calendar_year,
        date,
        tour,
        scores
    }){
        this.id = id,
        this.tournament_name = tournament_name,
        this.calendar_year = calendar_year,
        this.date = date,
        this.tour = tour,
        this.scores = scores
    }

    static async getTournament(tournamentId){
        const res = await axios.get(`${BASE_URL}/tournaments/${tournamentId}`)
        const {tournament} = res.data
        return new Tournament({
            id : tournament.id,
            tournament_name : tournament.tournament.name,
            calendar_year : tournament.calendar_year,
            date : tournament.date,
            tour : tournament.tour
        })
    }


}
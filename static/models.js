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
        const res = await axios.post(`${BASE_URL}/users/signup`, formData)
        const {user} = res.data
        
        return new User({id:user.id,
                        username:user.username,
                        teams : user.teams,
                        leagues : user.teams})
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

    async createLeague(league_name,start_date,end_date,privacy,golfer_count){
        const data = {league_name,start_date,end_date,privacy,golfer_count}
        const res = await axios.post(`${BASE_URL}/users/${self.id}/leagues/create`, data)
        const {league} = res.data
        return new League({
            id:league.id,
            league_name:league.league_name,
            start_date: league.start_date,
            end_date: league.end_date,
            privacy: league.privacy,
            golfer_count: league.golfer_count,
            teams: league.teams,
            golfers: league.golfers
        })
    }

    async joinLeague(league_id){
        const res = await axios.post(`${BASE_URL}/users/${self.id}/leagues/${league_id}`)
        const {league} = res.data
        return new League({
            id:league.id,
            league_name:league.league_name,
            start_date: league.start_date,
            end_date: league.end_date,
            privacy: league.privacy,
            golfer_count: league.golfer_count,
            teams: league.teams,
            golfers: league.golfers
        })
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
        teams=[],
        golfers=[]
    }){
        this.id = id,
        this.league_name = league_name,
        this.start_date = start_date,
        this.end_date = end_date,
        this.privacy = privacy,
        this.golfer_count = golfer_count,
        this.max_teams = max_teams,
        this.teams = teams.map(t => new Team(t))
        this.golfers = golfers.map(g => new Golfer(g))
    }

    static async newLeague(league_name,start_date,end_date,privacy,golfer_count){
        const data = {league_name,start_date,end_date,privacy,golfer_count}
        const res = await axios.post(`${BASE_URL}/leagues/create`, data)
        const {league} = res.data
        return new League({
            id:league.id,
            league_name:league.league_name,
            start_date: league.start_date,
            end_date: league.end_date,
            privacy: league.privacy,
            golfer_count: league.golfer_count,
            teams: league.teams,
            golfers: league.golfers
        })
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
            teams: league.teams,
            golfers: league.golfers
        })
    }


}

class PublicLeagueList{
    constructor(leagues){
        this.leagues = leagues
    }

    static async getPublicLeagues(){
        const res = await axios.get(`${BASE_URL}/leagues/public`)
        const leagues = res.data.leagues.map(l => new League(l))
        new PublicLeagueList(leagues)
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

    static async createTeam(team_name, league_id, user_id){
        const data = {team_name, league_id, user_id}
        const res = await axios.post(`${BASE_URL}/teams/create`, data)
        return new Team(res.data.team)
    }

    static async getTeam(teamId){
        const res = await axios.get(`${BASE_URL}/teams/${teamId}`)
        return new Team(res.data.team)
    }

    async addOrDeleteGolferToTeam(golfer, type){
        if(type == "ADD") {
            const res = await axios.post(`${BASE_URL}/teams/${this.id}/golfers/${golfer.id}`)
            this.golfers.push(golfer)
        }

        if(type == "DELETE") {
            const res = await axios.delete(`${BASE_URL}/teams/${this.id}/golfers/${golfer.id}`)
            this.golfers = this.golfers.filter(g => g !== golfer)
        }
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

class TeamList {
    constructor(teams) {
        this.teams = teams;
    }

    static async getTeamsInLeague(leagueId) {
        const res = await axios.get(`${BASE_URL}/leagues/${leagueId}/teams`);
        console.log(res)
        const teams = res.data.teams.map(t => {
            const golfers = t.golfers.map(g => {
                return new Golfer({
                    id: g.id,
                    first_name: g.first_name,
                    last_name: g.last_name
                });
            });
            return new Team({
                id: t.id,
                team_name: t.team_name,
                user_id: t.user_id,
                league_id: t.league_id,
                created_at: t.created_at,
                golfers: golfers
            });
        });

        return new TeamList(teams);
    }
}







class Golfer {
    constructor({
        id,
        first_name,
        last_name
        
    }){
        this.id = id,
        this.first_name = first_name,
        this.last_name = last_name
    }

    static async getGolfer(golferId){
        const res = await axios.get(`${BASE_URL}/golfers/${golferId}`)
        const {golfer} = res.data
        return new Golfer({
            id:golfer.id,
            first_name: golfer.first_name,
            last_name: golfer.last_name
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
                last_name: golfer.last_name
            })
        })
        return new GolferList(golfers)
    }

    static async getAvailableGolfers(league_id){
        const res = await axios.get(`${BASE_URL}/leagues/${league_id}/golfers/available`)
        console.log(res)
        const golfers = res.data.golfers.map(g => {
            return new Golfer({
                id:g.id,
                first_name: g.first_name,
                last_name: g.last_name
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
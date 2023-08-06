let currentLeague = ""
let golferList = ""
let $leagueLinks = $('.league-links')
const $availableGolfers = $('#available-golfers')
const $draftOrder = $('#draft-order')
const $queue = $('#queue')
const $teamGolfers = $('#team-golfers')


$leagueLinks.on("click", storeLeaguetoSessionStorage)

async function storeLeaguetoSessionStorage(evt){
    console.log("CLICKED")
    const leagueId = evt.target.dataset.league_id
    sessionStorage.setItem("leagueId", leagueId)
}

async function instantiateCurrentLeague(){
    const leagueId = sessionStorage.getItem("leagueId")
    currentLeague = await League.getLeague(leagueId)
    console.log(currentLeague.league_name)
}

async function instantiateCurrentTeam(){
    let team = currentUser.teams.find(t => t.league_id == currentLeague.id)
    currentTeam = await Team.getTeam(team.id)

}


async function putDraftOrderOnPage(){
    $draftOrder.empty()
    leagueTeams = await TeamList.getTeamsInLeague(currentLeague.id)
    for (let team of leagueTeams.teams){
        let $team = generateTeamMarkUp(team)
        $draftOrder.append($team)
    }
}

//Need to add functionality to control the sequence of which team can draft. Only one team can draft a golfer at a time. Need way to show users who is currently drafting and when their turn is.

function generateTeamMarkUp(team){
    return `<li>${team.team_name}</li>`
}


async function putAvailableGolfersOnPage(){
    const leagueId = sessionStorage.getItem("leagueId")
    $availableGolfers.empty()
    golferList = await GolferList.getAvailableGolfers(leagueId)
    for (let golfer of golferList.golfers){
        let $golfer = generateAvailableGolferMarkUp(golfer)
        $availableGolfers.append($golfer)
    }
}


function generateAvailableGolferMarkUp(golfer){
       return $(`<li data-available_golfer_id="${golfer.id}" class="available-golfer">${golfer.first_name} ${golfer.last_name}</li>`)
    }


$availableGolfers.on('click','li',addGolferToTeam)


async function addGolferToTeam(evt){
    const golferId = evt.target.dataset.available_golfer_id
    let golfer = golferList.golfers.find(g => g.id == golferId)
    await currentTeam.addOrDeleteGolferToTeam(golfer, "ADD")
    putAvailableGolfersOnPage()
    showGolfersOnTeam()

}

async function showGolfersOnTeam(){
    $teamGolfers.empty()
    for(let golfer of currentTeam.golfers){
        let $golfer = generateGolferOnTeamMarkup(golfer)
        $teamGolfers.append($golfer)
    }
}



function generateGolferOnTeamMarkup(golfer){
    return $(`<li data-drafted_golfer_id=${golfer.id} class="drafted golfer"> ${golfer.first_name} ${golfer.last_name} </li>`)
}

$(document).ready(draft_page_load)

async function draft_page_load(){
    await instantiateCurrentLeague()
    await putDraftOrderOnPage()
    await putAvailableGolfersOnPage()
    await instantiateCurrentTeam()
    await showGolfersOnTeam()
}
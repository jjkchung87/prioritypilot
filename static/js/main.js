// Define global variables *****************************************************************************

let currentUser = ""
let leagueTeams = ""
let currentTeam = ""
let currentLeague = ""

const socket = io('http://127.0.0.1:5000');


const $signupForm = $('#signup_form')
const $loginForm = $('#login_form')
const $logoutForm = $('#logout_form')
const $leagueLinks = $('.league-links')




// CURRENT USER: Store in session storage and instantiate***********************************************************

$loginForm.on("submit",handleLogin)
$signupForm.on("submit",handleSignUp)
$logoutForm.on("submit",handleLogout)

//Authenticates user. If successful, stores in client-side Session Storage
async function handleLogin(){
    const username = $('#login-username').val()
    const password = $('#login-password').val()
    currentUser = await User.authenticate(username, password)

    storeLoggedInUserToSession()
}


async function handleSignUp(evt){
    evt.preventDefault()

    const formData = $signupForm.serialize()


    try {
        const response = await User.signUp(formData);
        console.log(response)
        if (response.success) {
            currentUser = response.user;
            storeLoggedInUserToSession();
            console.log(currentUser);
            window.location.href = '/golfantasy';  // Redirect to homepage
        } else {
            console.error("Signup failed:", response.errors);
        }
    } catch (error) {
        console.error(error.response.data);
    }  
}

async function storeLoggedInUserToSession(){
    if (currentUser) {
        sessionStorage.setItem("id",currentUser.id)
    }
}


async function instantiateCurrentUser(){
    const id = sessionStorage.getItem("id")
    if(!id) return false;
    currentUser = await User.retrieveCurrentUser(id)
}


async function handleLogout(){
    sessionStorage.clear()
}


// CURRENT LEAGUE: Store in session storage and instantiate***********************************************************

$leagueLinks.on("click", storeLeaguetoSessionStorage)

async function storeLeaguetoSessionStorage(evt){
    console.log("CLICKED")
    const leagueId = evt.target.dataset.league_id
    sessionStorage.setItem("leagueId", leagueId)
}

async function instantiateCurrentLeague(){
    const leagueId = sessionStorage.getItem("leagueId")
    currentLeague = await League.getLeague(leagueId)
    draftPickIndex = currentLeague.draft_pick_index
    draftPickCount = currentLeague.draft_pick_count
    draftCompleted = currentLeague.draft_completed
}

async function instantiateCurrentTeam() {
    if (currentUser && currentLeague) {
        let team = currentUser.teams.find(t => t.league_id == currentLeague.id);
        if (team) {
            currentTeam = await Team.getTeam(team.id);
        }
    }
}

async function initializePage() {
    await instantiateCurrentUser();
    await instantiateCurrentLeague();
    await instantiateCurrentTeam();
    // picksPerTeam = currentLeague.golfer_count
    // draftPickIndex = currentLeague.draft_pick_index
    // Now you can continue with the rest of your logic that depends on these values
}

instantiateCurrentUser()
instantiateCurrentLeague()

// DRAFT PAGE LOGIC **************************************************************************************************************

$(document).ready(async function() {
await initializePage()

console.log('start of draft script')

//Define Draft Variables ****************************************************************************************************************

    let picksPerTeam = 0
    let draftPickIndex = 0
    let draftPickCount = 0
    let draftCompleted = false

    picksPerTeam = currentLeague.golfer_count
    draftPickIndex = currentLeague.draft_pick_index


//Define Draft Functions ****************************************************************************************************************

    function addDraftOrderToPage(teams){
        $('#draft-order').empty()
        for(let team of teams){
            let $teamHTML = ""
            if (draftPickIndex % currentLeague.teams.length !== currentLeague.draft_order.indexOf(team.id)) {
                $teamHTML  = `<div class="draft-pick-team">${team.team_name}</div>`;
            } else {
                $teamHTML =  `<div class="draft-pick-team bg-primary text-white">${team.team_name} <i class="fa-regular fa-circle-left"></i></div>`;
            }
            $('#draft-order').append($teamHTML)
        }
    }

    function updateDraftPickCounter(draft_pick_count, max_draft_picks){
        $('#draft-pick-counter').text("");
        $('#draft-pick-counter').text(`${draft_pick_count} / ${max_draft_picks}`);
    }

    function updateDraftedGolfers(drafted_golfers){
        $('#drafted-golfers').empty()
        for(let golfer of drafted_golfers){
            const golferHTML = `<div><img class="golfer-image" src="${golfer.golfer_image_url}"> ${golfer.first_name} ${golfer.last_name}</li>`
        $('#drafted-golfers').append(golferHTML)
        }    
    }

    function updateTeamGolfers(team_golfers){
        $('#team-golfers').empty()
        for(let team of team_golfers){
            let $teamDiv = ""
            
            if(team.team_name == currentTeam.team_name){
                $teamDiv = `<div class="col col-6 team-golfers-team d-flex flex-column align-items-start" data-team_id="${team.id}">
                <p class="bg-secondary text-white"> ${team.team_name}</p>`
            } else{
                $teamDiv = `<div class="col col-6 team-golfers-team d-flex flex-column align-items-start" data-team_id="${team.id}">
                <p> ${team.team_name}</p>`
            }
            
            for(let golfer of team.golfers){
                let $golferDiv = `<div><img class="golfer-image" src="${golfer.golfer_image_url}">${golfer.first_name} ${golfer.last_name}</div>`
                $teamDiv = $teamDiv+$golferDiv
            }

        $teamDiv = $teamDiv + '</div>'   
        
        $('#team-golfers').append($teamDiv)
            
        }
    }


    // function updateAvailableGolfers(available_golfers){
    //     $('#available-golfers').empty()
    //     for(let golfer of available_golfers){
    //         const golferHTML = `<tr>
    //                                 <td data-golfer_id="${golfer.id}">${golfer.owgr}</td>
    //                                 <td data-golfer_id="${golfer.id}">
    //                                     <img class="golfer-image" src="${golfer.golfer_image_url}">
    //                                     ${golfer.first_name} ${golfer.last_name}
    //                                 </td>
    //                             </tr>`
    //         $('#available-golfers').append(golferHTML)
    //     }
    // }

//Add draft order to page ************************************************************************************************************************

    addDraftOrderToPage(currentLeague.teams)


//Draft pick event listener ********************************************************************************************************
    
    $('#available-golfers').on('click','tr', function(evt) {
        console.log("CLICKED")
        if (draftCompleted) {
                return; // All rounds of picks are done, exit early
            }

        if (draftPickIndex % currentLeague.teams.length !== currentLeague.draft_order.indexOf(currentTeam.id)) {
                return; // Not the current team's turn, exit early
            }
        
        const $tr = $(evt.target).closest('tr');    
        const golfer_id = parseInt($tr.data('golfer_id'))
        const team_id = currentTeam.id;
        const league_id = currentLeague.id;
        const data = { golfer_id, team_id, league_id, draftPickIndex, draftPickCount };


        // Emit draft pick event to the server
        socket.emit('make_draft_pick', data);
    });

    
    socket.on('golfer_drafted', function(data) {
        const picked_golfer = data.picked_golfer;
        // const available_golfers = data.available_golfers;
        const drafted_golfers = data.drafted_golfers;
        const team_golfers = data.team_golfers;
        draftPickCount = data.draft_pick_count;
        const maxDraftPicks = data.max_draft_picks;
        draftPickIndex = data.draft_pick_index;
        draftCompleted = data.draft_completed;

        const $pickedGolfer = $(`#available-golfers tr[data-golfer_id="${picked_golfer.id}"]`)
        $pickedGolfer.remove()
        addDraftOrderToPage(currentLeague.teams)
        updateDraftPickCounter(draftPickCount, maxDraftPicks)
        updateDraftedGolfers(drafted_golfers)
        updateTeamGolfers(team_golfers)
        // updateAvailableGolfers(available_golfers)
    
        if(draftCompleted){
            $('#draft-complete-modal').modal('show')
        }

    });

    console.log('end of draft script')

})





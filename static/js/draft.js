$(document).ready(async function() {
    await initializePage()
    
    console.log('start of draft script')
    
    //**********************************************************************************************************************************
    //Define variables
    
        let picksPerTeam = 0
        let draftPickIndex = 0
        let draftPickCount = 0
        let draftCompleted = false
    
        picksPerTeam = currentLeague.golfer_count
        draftPickIndex = currentLeague.draft_pick_index
    
    //**********************************************************************************************************************************
    //Instantiate socket
    
        const socket = io('http://127.0.0.1:5000');
    
    //**********************************************************************************************************************************
    //Define functions
    
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
            $('#draft-pick-counter').empty();
            const $draftPickCounterHTML = `
            <p><b>Draft Picks Made: </b>${draft_pick_count} / ${max_draft_picks}</p>`
            $('#draft-pick-counter').append($draftPickCounterHTML)
        }
    
        function updateDraftedGolfers(drafted_golfers){
            $('#drafted-golfers').empty()
            for(let golfer of drafted_golfers){
                const golferHTML = `<li>${golfer.first_name} ${golfer.last_name}</li>`
            $('#drafted-golfers').append(golferHTML)
            }    
        }
    
        function updateAvailableGolfers(available_golfers){
            $('#available-golfers').empty()
            for(let golfer of available_golfers){
                const golferHTML = `<tr data-golfer_id="${golfer.id}"><td data-golfer_id="${golfer.id}">${golfer.owgr}</td><td data-golfer_id="${golfer.id}"><img class="golfer-image" src="${golfer.golfer_image_url}">${golfer.first_name} ${golfer.last_name}</td></tr>`
                $('#available-golfers').append(golferHTML)
            }
        }
    
        function updateTeamGolfers(team_golfers){
            $('#team-golfers').empty()
            for(let team of team_golfers){
                let $teamDiv = ""
                
                if(team.team_name == currentTeam.team_name){
                    $teamDiv = `<div class="col col-6 team-golfers-team" data-team_id="${team.id}">
                    <p class="bg-secondary text-white"> ${team.team_name}</p>`
                } else{
                    $teamDiv = `<div class="col col-6 team-golfers-team" data-team_id="${team.id}">
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
    
    //**********************************************************************************************************************************
    //Add draft order to page
    
        addDraftOrderToPage(currentLeague.teams)
    
    //**********************************************************************************************************************************
    //Draft pick event listener
        
        $('#available-golfers').on('click','td', function(evt) {
            console.log("CLICKED")
            if (draftCompleted) {
                    return; // All rounds of picks are done, exit early
                }
    
            if (draftPickIndex % currentLeague.teams.length !== currentLeague.draft_order.indexOf(currentTeam.id)) {
                    return; // Not the current team's turn, exit early
                }
            
            const golfer_id = parseInt(evt.target.dataset.golfer_id)
            const team_id = currentTeam.id;
            const league_id = currentLeague.id;
            const data = { golfer_id, team_id, league_id, draftPickIndex, draftPickCount };
    
            console.log(data)
    
            // Emit draft pick event to the server
            socket.emit('make_draft_pick', data);
        });
    
        
        socket.on('golfer_drafted', function(data) {
            const available_golfers = data.available_golfers;
            const drafted_golfers = data.drafted_golfers;
            const team_golfers = data.team_golfers;
            draftPickCount = data.draft_pick_count;
            const maxDraftPicks = data.max_draft_picks;
            draftPickIndex = data.draft_pick_index;
            draftCompleted = data.draft_completed;
    
            addDraftOrderToPage(currentLeague.teams)
            updateDraftPickCounter(draftPickCount, maxDraftPicks)
            updateDraftedGolfers(drafted_golfers)
            updateAvailableGolfers(available_golfers)
            updateTeamGolfers(team_golfers)
        
            console.log("next pick:", draftPickIndex, "draft pick count:", draftPickCount, "draft status:", draftCompleted)
    
            if(draftCompleted){
                $('#draft-complete-modal').modal('show')
            }
    
        });
        console.log('end of draft script')
    
    })
    
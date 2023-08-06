let currentUser = ""
let leagueTeams = ""
let currentTeam = ""


const $signupForm = $('#signup_form')
const $loginForm = $('#login_form')
const $logoutForm = $('#logout_form')




// CURRENT USER *****************************************************************************

$loginForm.on("submit",handleLogin)
$signupForm.on("submit",handleSignUp)
$logoutForm.on("submit",handleLogout)


async function handleLogin(){

    const username = $('#login-username').val()
    const password = $('#login-password').val()
    currentUser = await User.authenticate(username, password)

    storeLoggedInUserToSession()
}


async function handleSignUp(evt){
    evt.preventDefault()

    const formData = $signupForm.serialize()

    console.log(formData)

    try{
        currentUser = await User.signUp(formData)
        storeLoggedInUserToSession()
        console.log(currentUser)
    } catch (error){
        console.error(error.response.data)
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
    console.log(currentUser)
}


async function handleLogout(){
    sessionStorage.clear()
}




instantiateCurrentUser()

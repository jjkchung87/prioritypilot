import { useState, useEffect } from 'react'
import { UserContext } from './context/UserContext'
import { ProjectContext , ProjectsContext } from './context/ProjectContext'
import MainNavbar from './components/MainNavbar'
import LoginForm from './components/LoginForm'
import RegistrationForm from './components/RegistrationForm'
import UserPage from './components/UserPage'
import { Routes, Route, useNavigate } from 'react-router-dom'
import useLocalStorage from './hooks/useLocalStarage'
import UserApi from './api'
import { decodeToken } from 'react-jwt';
import './App.css'

function App() {
  const navigate = useNavigate()
  const [currentUser, setCurrentUser] = useState(null)
  const [projects, setProjects] = useState(null)
  const [currentProject, setCurrentProject] = useState(null)
  const [token, setToken] = useLocalStorage("token")

  useEffect(
    function loadUserInfo() {
      async function getCurrentUser() {
        if (token) {
          try {
            const user = decodeToken(token)
            // put the token on the Api class so it can use it to call the API.
            UserApi.token = token;
            // finds current user info by user_id from token
            let currUser = await UserApi.getCurrentUser(user.sub);
            setCurrentUser(currUser.user);  
            setProjects(currUser.user.projects)
          } catch (err) {
            console.error("App loadUserInfo: problem loading", err);
            setCurrentUser(null);
          }}}
      getCurrentUser();
    }, [token]);

  // Handles site-wide signup.
  async function register(signupData) {
    try {
      let token = await UserApi.register(signupData);
      setToken(token);
      return { success: true };
    } catch (errors) {
      console.error("signup failed", errors);
      return { success: false, errors };
    }
  }

  //Handles site-wide login
  async function login(data) {
    try {
      let token = await UserApi.login(data);
      setToken(token);
      return { success: true  };
    } catch (errors) {
      console.error("Invalid Credentials", errors);
      return { success: false, errors };
    }
  }

  //Handles site-wide logout
  async function logout() {
    setCurrentUser(null);
    setCurrentProject(null);
    setProjects(null);
    setToken(null);
    navigate('/')
  }
  return (
    <>
      <UserContext.Provider value={{ currentUser }}>
      <ProjectContext.Provider value={{ currentProject, setCurrentProject }}>
      <ProjectsContext.Provider value={{ projects, setProjects }}>
        <MainNavbar logout={logout}/>
        <Routes>
          <Route path='/' element={<LoginForm login={login}/>} />
          <Route path='/register' element={<RegistrationForm register={register}/>} />
          <Route path='/my_projects' element={<UserPage logout={logout} />} />
        </Routes> 
      </ProjectsContext.Provider>
      </ProjectContext.Provider>
      </UserContext.Provider>
    </>
  )
}

export default App;

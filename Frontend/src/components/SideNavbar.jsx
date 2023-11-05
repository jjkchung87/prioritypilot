import { Icon } from 'semantic-ui-react';
import { useState, useContext, useEffect} from 'react'
import TeamMember from './TeamMember';
import { UserContext } from '../context/UserContext'
import { ProjectContext } from '../context/ProjectContext'
import UserApi from '../api'

function SideNavbar({userTasks}) {
  const { currentUser } = useContext(UserContext)
  const { currentProject } = useContext(ProjectContext)

  const [teamView, setTeamView] = useState("Project Team")
  const [teamMemberCards, setTeamMemberCards] = useState([])

  useEffect(() => {
    const controller = new AbortController()
    async function fetchUsers() {
      let users = null;
      try {
        if (teamView === 'Project Team') {
          if (currentProject) {
            let res = await UserApi.getUsersByProject(currentProject.id)
            users = res.data.users
          }
        } else {
          let res = await UserApi.getSubs(currentUser.id)
          users = res.data.users
        }
        if (users) {
          setTeamMemberCards(users.filter(u => u.id !== currentUser.id))
        }
      } catch (error){
        console.error('Error fetching team users:', error)
      } 
    }
    fetchUsers()
    return () => {
      controller.abort()
    }
  }
  ,[teamView, currentProject, userTasks])
  
  const handleTeamViewChange = (e) => {
    setTeamView(e.target.value)
  }

 
  return (
    <div className="wrapper sidebar" >
      <div className="team-members" style={{textAlign:"center"}}>
        <select className="select-project" value={teamView} onChange={handleTeamViewChange}>
          <option value="Project Team">Project Team</option>
          <option value="Your Team">Your Team</option>
        </select>
        <p>
          <span className="status-color"><Icon color='black' name='square' />Complete </span>
          <span className="status-color"><Icon color='blue' name='square' />In Progress </span>
          <span className="status-color"><Icon color='grey' name='square' />Not Started </span>
        </p>
        <div className="SideNavbar-TeamCards">
          {teamMemberCards && teamMemberCards.map(member => (
            <TeamMember  key={member.id} member={member}/>
          ))}
        </div>
      </div>
    </div>
  )
  }
  export default SideNavbar
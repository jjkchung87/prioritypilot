import SideNavbar from './SideNavbar'
import ProjectDropdown from './ProjectDropdown'
import TodaysProgressTable from './TodaysProgressTable'
import PollingCountDown from './PollingCountDown'
import ProjectProgressTable from './ProjectProgressTable'
import MainTaskScreen from './MainTaskScreen'
import { useContext, useEffect, useState} from 'react'
import { UserContext } from '../context/UserContext'
import { useNavigate } from 'react-router-dom'
import UserApi from '../api'
import { ProjectContext } from '../context/ProjectContext'

function UserPage({ logout }) {
  const { currentUser } = useContext(UserContext)
  const { currentProject } = useContext(ProjectContext)
  const [userTasks, setUserTasks ] = useState([])
  const [isLoading, setIsLoading ] = useState(true)
  const navigate = useNavigate()

  useEffect (() => {
    if (!currentUser) navigate('/') 
  })

  useEffect(
    function getAllTasks() {
      if (currentUser) {
        async function getUsersTasks() {
          //request all the tasks for the user
          let res = await UserApi.getUsersTasks(currentUser.id)
          //if no current project - display all tasks
          setUserTasks([...res.tasks])
          setIsLoading(false)
        }
        getUsersTasks()
      } else {
        setIsLoading(true)
      }
      if (!userTasks) setIsLoading(true)
  }, [currentProject, currentUser])

  const deleteTask = async (task_id) => {
    await UserApi.deleteTask(task_id)
    setUserTasks([...userTasks.filter(t => t.id !== task_id)])
  }

  return (
    <>
    {isLoading ? <div>Loading</div> :
    <div className="user-page">
      <SideNavbar tasks={userTasks} />
      <div className='user-dashboard'>
        <div className='status-tables'>
          <TodaysProgressTable tasks={userTasks}/>
          <ProjectProgressTable userTasks={userTasks}/>
          <PollingCountDown />
        </div>
        <div className='project-table'>
          <ProjectDropdown />
          <MainTaskScreen userTasks={userTasks} setUserTasks={setUserTasks} deleteTask={deleteTask}/>
        </div>
      </div>
    </div>}
    </>
  )
}

export default UserPage
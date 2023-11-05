import { Tab, Header } from 'semantic-ui-react'
import TaskCard from './TaskCard'
import NewTaskForm from './NewTaskForm'
import { useContext, useEffect, useState } from 'react'
import { ProjectContext } from '../context/ProjectContext'
import {v4 as uuid} from 'uuid';
import Carousel from 'react-grid-carousel'

function MainTaskScreen({userTasks, setUserTasks, deleteTask}) {
  const { currentProject } = useContext(ProjectContext)
  let currentTime = new Date()
  let [tasks, setTasks] = useState(userTasks)

  useEffect(() => {
    if (currentProject) {
      setTasks([...currentProject.tasks])
    } else {
      setTasks([...userTasks])
    }
  }, [currentProject, userTasks])

  //tabs for tasks
  const myPanes = [
    //All User's Tasks for a current project or all tasks if project not selected
    { menuItem: 'All Tasks', render: () => <Tab.Pane className='tab-pane'>
      {currentProject && <Header>Project: <span className='tab-project-name'>{currentProject.project_name}</span></Header>}
      {tasks.filter(task => task.status !== 'Complete').length > 0 ?
        <Carousel cols={2} rows={3} gap={10} loop className='carousel'>
          {tasks.sort(function(a,b) {
            return new Date(a.end_date) - new Date(b.end_date)}).filter(task => task.status !== 'Complete').map(task => (
            <Carousel.Item className='carousel-item' key={uuid()} >
              <TaskCard task={task} setTasks={setUserTasks} tasks={tasks} deleteTask={deleteTask}/>
            </Carousel.Item>))}
        </Carousel> : 
        <Header>You do not have any tasks.</Header> }
        </Tab.Pane>},

    //Tasks that are due today
    { menuItem: 'Today', render: () => <Tab.Pane className='tab-pane'>
      {currentProject && <Header>Project: <span className='tab-project-name'>{currentProject.project_name}</span></Header>}
      {tasks.filter(task => (
         new Date(task.end_date).getDate() <= new Date().getDate() && 
         new Date(task.end_date).getMonth() === new Date().getMonth() &&
         task.status !== 'Complete')).length > 0 ?
        <Carousel cols={2} rows={3} gap={10} loop className='carousel'>
          {tasks.sort(function(a,b) {
            return new Date(a.end_date) - new Date(b.end_date)}).filter(task => (
            new Date(task.end_date).getDate() <= new Date().getDate() && 
            new Date(task.end_date).getMonth() === new Date().getMonth() &&
            task.status !== 'Complete')).map(task => (
              <Carousel.Item className='carousel-item' key={uuid()} >
                <TaskCard task={task} setTasks={setUserTasks} tasks={tasks} deleteTask={deleteTask}/>
              </Carousel.Item>))}
        </Carousel>:
        <Header>You do not have any tasks that are due today.</Header> }
        </Tab.Pane> },

    //Tasks that are due this week
    { menuItem: 'This Week', render: () => <Tab.Pane className='tab-pane'>
      {currentProject && <Header>Project: <span className='tab-project-name'>{currentProject.project_name}</span></Header>}
      {tasks.filter(task => (
        new Date(task.end_date).getDate() <= new Date(currentTime.setDate(currentTime.getDate() - currentTime.getDay()+6)) &&
        task.status !== 'Complete')).length > 0 ?
        <Carousel cols={2} rows={3} gap={10} loop className='carousel'>
          {tasks.sort(function(a,b) {
            return new Date(a.end_date) - new Date(b.end_date)
          }).filter(task => (
            new Date(task.end_date).getDate() <= new Date(currentTime.setDate(currentTime.getDate() - currentTime.getDay()+6)).getDate() &&
            task.status !== 'Complete')).map(task => (
              <Carousel.Item className='carousel-item' key={uuid()} >
                <TaskCard task={task} setTasks={setUserTasks} tasks={tasks} deleteTask={deleteTask}/>
              </Carousel.Item>))}
        </Carousel> :
        <Header>You do not any tasks that are due this week.</Header> }
        </Tab.Pane> }, 

    //Completed Tasks
    { menuItem: 'Completed Tasks', render: () => <Tab.Pane className='tab-pane'>
      {currentProject && <Header>Project: <span className='tab-project-name'>{currentProject.project_name}</span></Header>}
      {tasks.filter(task => task.status === 'Complete').length > 0 ?
        <Carousel cols={2} rows={3} gap={10} loop className='carousel'>
          {tasks.sort(function(a,b) {
            return new Date(a.end_date) - new Date(b.end_date)}).filter(task => task.status === 'Complete').map(task => (
            <Carousel.Item className='carousel-item' key={uuid()} >
              <TaskCard task={task} setTasks={setUserTasks} tasks={tasks} deleteTask={deleteTask}/>
            </Carousel.Item>))}
        </Carousel> :
        <Header>You have not completed any tasks.</Header> }
        </Tab.Pane> }, 

    //Renders form to add a task
    { menuItem: '+Add New Task', render: () => (
      <Tab.Pane className='tab-pane'><NewTaskForm/></Tab.Pane> )}]

  return (
    <div className="main-screen wrapper">
      <Tab panes={myPanes} />
    </div>
  )
}
  
export default MainTaskScreen
import { useEffect, useState } from "react"
import { Header, Icon } from "semantic-ui-react"

function TodaysProgressTable({tasks}) {
  const [progress, setProgress] = useState(null)
  const [todayTasks, setTodayTasks] = useState(tasks)
  
  useEffect(() => {
    //first find tasks that are due toda or past due with status not 'Complete'
    const todayTasks = tasks.filter(task => (
      new Date(task.end_date).getDate() <= new Date().getDate() && 
      new Date(task.end_date).getMonth() === new Date().getMonth()))
    let complete = ''
    let inProgress = ''
    let notStarted = ''
    if (todayTasks.length > 0) {
      for (let task of todayTasks) {
        if (task.status === 'Complete') {
          complete ++
        } else if (task.status === 'In Progress') {
          inProgress++
        } else {
          notStarted++
        }
      }
      setTodayTasks([...todayTasks])
      setProgress({complete: complete, inProgress: inProgress, notStarted: notStarted})
    } else {
      setProgress(null)
    }
    
}, [tasks])

  return (
    <div className="table">
      {todayTasks.length === 0 || !progress ? <Header>Not tasks for today</Header> : <>
      <Header>Today's Progress</Header>
      <p>Today's Tasks: {todayTasks.length}</p>
      <p>
          <span className="status-color"><Icon color='black' name='square' />Complete </span>
          <span className="status-color"><Icon color='blue' name='square' />In Progress </span>
          <span className="status-color"><Icon color='grey' name='square' />Not Started </span>
      </p>
      <div className="progress-bar">
        <div className="completed-tasks" style={{width: `${progress.complete/todayTasks.length*100}%`}}>{progress.complete}</div>
        <div className="in-progress-tasks" style={{width: `${progress.inProgress/todayTasks.length*100}%`}}>{progress.inProgress}</div>
        <div className="not-started-tasks" style={{width: `${progress.notStarted/todayTasks.length*100}%`}}>{progress.notStarted}</div>
			</div>
      </>}
    </div>
  )
  }
  
export default TodaysProgressTable
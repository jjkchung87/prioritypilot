import React, { useState, useContext, useEffect } from 'react'
import { UserContext } from '../context/UserContext'
import DatePicker from 'react-datepicker'
import './Forms.css'
import Logo from "../assets/pp_logo.png"
import { Button, Icon, Table } from 'semantic-ui-react'
import AiTipsModal from './AiTipsModal';
import UserApi from '../api'

function Modal({ closeModal, resetTimer }) {
  const { currentUser } = useContext(UserContext);
  const [showAiModal, setShowAiModal] = useState({status: false, task: null})
  const [tasksForToday, setTasksForToday] = useState(null)

  useEffect(()=> {
    const controller = new AbortController()
    async function getUsersTasks() {
      try {
        const res = await UserApi.getUsersTasks(currentUser.id)
        const tasks = res.tasks.filter(t => (
          new Date(t.end_date).getDate() <= new Date().getDate() && 
          new Date(t.end_date).getMonth() === new Date().getMonth() &&
          t.status !== 'Complete'))
        setTasksForToday([...tasks])
      } catch (err) {
        console.error("Problem loading today's tasks", err)
        closeModal()
      }
    }
    getUsersTasks()
    return () => {
      controller.abort()
    }
  }, [])
    
  // // Function to filter and retrieve tasks that meet the criteria
  // const getTasksForToday = () => {
  //   if (currentUser && currentUser.projects) {
  //     // Get today's date in "yyyy-mm-dd" format
  //     const today = new Date().toISOString().split('T')[0]; 
  //     const tasksForToday = currentUser.projects.reduce((acc, project) => {
  //       const projectTasks = project.tasks.filter(
  //         (task) =>
  //           new Date(task.end_date) <= new Date(today) && task.status !== 'Complete'
  //       );
  //       return acc.concat(projectTasks);
  //     }, []);
  //     return tasksForToday;
  //   }
  //   return [];
  // };

  // const tasksForToday = getTasksForToday();

  // // State to track the selected status and adjusted end_date for each task
  // const [taskData, setTaskData] = useState(
  //   tasksForToday.reduce((data, task) => {
  //     data[task.id] = {
  //       status: task.status,
  //       end_date: new Date(task.end_date).toLocaleString('en-US', {
  //         weekday: 'short',
  //         year: 'numeric',
  //         month: 'short',
  //         day: 'numeric',
  //       }),
  //     };
  //     return data;
  //   }, {})
  // );

  // Event handler to update the task's status
  const handleStatusChange = async (task, event) => {
    const newStatus = event.target.value;
    setTasksForToday(tasksForToday.map(t => {
      if (t.id === task.id) {
        return {...t, status: newStatus}
      } else {
        return t
      }}))
    // You can add logic to update the task's status in the database/API here.
    task.status = newStatus
    try {
      await UserApi.editTask(task, task.project_id, task.id);
    } catch(err) {
      console.error('Problem Updating Deadline', err)
    }
  };

    // Event handler to update the task's end_date
    const handleEndDateChange = async (task, newEndDate) => {
        setTasksForToday(tasksForToday.map(t => {
          if (t.id === task.id) {
            return {...t, end_date: newEndDate}
          } else {
            return t
          }}))
        // You can add logic to update the task's end_date in the database/API here.
        task.end_date = newEndDate
        try {
          await UserApi.editTask(task, task.project_id, task.id);
        } catch(err) {
          console.error('Problem Updating Deadline', err)
        }
        
    };
  
  const handleClosePoll = () => {
    closeModal()
    resetTimer()
  }
  console.log('todays tasks', tasksForToday)
  return (
    <div className="modal-background">
      <div className='modal-content'>
        <Button className='close-window' icon
                onClick={handleClosePoll}
                size="tiny">
          <Icon name="close"></Icon>
        </Button>
        {showAiModal.status && <AiTipsModal task={showAiModal.task} closeModal={()=>setShowAiModal(false)} />}
        {tasksForToday ? (
          <>
            <h2 className='update-time-header'>Time for an update!</h2>
            <table className="table-style countdown-modal-table">
              <thead>
                <tr>
                  <td>Project</td>
                  <td>Task</td>
                  <td>Deadline</td>
                  <td>Status</td>
                  <td>AI Navigation</td>
                </tr>
              </thead>
              <tbody>
                {tasksForToday.map((task) => (
                  <tr key={task.id}>
                    <td className='project-name'>
                      {currentUser.projects.filter((p) => p.id === task.project_id)[0].project_name}
                    </td>
                    <td className='poll-task-name'>{task.task_name}</td>
                    <td >
                      <DatePicker
                        className='poll-date'
                        selected={new Date(task.end_date)}
                        onChange={(date) => handleEndDateChange(task, date, task.project_id)}
                        dateFormat="eee, dd MMM yyyy"
                      />
                      {/* <DatePicker name='end_date' showTimeSelect filterDate={past} value={formData.end_date} selected={formData.end_date} onChange={handleInputChange} />  */}
                    </td>
                    <td >
                      <select
                      className='poll-select'
                        value={task.status}
                        onChange={(e) => handleStatusChange(task, e)}
                      >
                        <option value="Not Started">Not Started</option>
                        <option value="In Progress">In Progress</option>
                        <option value="Complete">Complete</option>
                      </select>
                    </td>
                    <td className='poll-image'>
                      <img
                        className="Modal-logo"
                        src={Logo}
                        alt='PriorityPilot_Logo'
                        onClick={() => setShowAiModal({ status: true, task: task })}
                      />
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </>
) : (
  <h2>You are doing great! No tasks are due today!</h2>
)}

        </div>
      </div>
    )  
}

export default Modal

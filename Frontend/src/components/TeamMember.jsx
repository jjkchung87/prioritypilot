import React, { useState } from 'react';
import "./TeamMember.css"

const TeamMember = ({member}) => {
  const [nudged, setNudged] = useState(false)

  console.log(member)
  //Last Update calculations
  const targetDate = new Date(member.latest_update); //date object
  const today = new Date(); // date object
  const timeDifference = today - targetDate;
  const daysDifference = Math.floor(timeDifference / (1000 * 60 * 60 * 24));
  const formattedDate = new Date(member.latest_update).toLocaleDateString('en-US');
  
  //Progress calculation
  const progress = Math.floor(member.completed_task_count/member.total_task_count * 100)
  const notStartedProgress = member.total_task_count===0 ? '' : Math.floor(member.not_started_task_count/member.total_task_count*100)
  const inProgressProgress = member.total_task_count===0 ? '' : Math.floor(member.in_progress_task_count/member.total_task_count*100)
  const completedProgress = member.total_task_count===0 ? '' : Math.floor(member.completed_task_count/member.total_task_count*100)
  
  const handleNudge = ()=> {
    setNudged(true)
  }

  return (
    <div className="TeamMember" style={{ textAlign: "left" }}>
      <img src={member.profile_img} className="TeamMember-img" alt='user_image'/>
      <div className="TeamMember-info">
        <div><b>{member.firstName} {member.lastName}</b></div> 
        <div>{member.role}</div>
        <div className="progress-bar">
          <div className="completed-tasks" style={{ width: `${completedProgress}%`, textAlign:"center" }}>
            {member.completed_task_count > 0 ? member.completed_task_count : ''}
          </div>
          <div className="in-progress-tasks" style={{ width: `${inProgressProgress}%`, textAlign:"center" }}>
          {member.in_progress_task_count > 0 ? member.in_progress_task_count : ''}
          </div>
          <div className="not-started-tasks" style={{ width: `${notStartedProgress}%`, textAlign:"center" }}>
          {member.not_started_task_count > 0 ? member.not_started_task_count : ''}
          </div>
        </div>
        <div className="last-update">
          {daysDifference > 7 ? (
          <>
            <span style={{ color: "red", fontSize:"10px" }}>
              <b>Last update:</b> {formattedDate}
            </span>
            { nudged ? (<div>nudged!</div>) : (<button onClick={handleNudge}>Nudge</button>)}
          </>
          ) : (
          <span style={{ fontSize:"10px"}}>
            <b>Last update:</b> {formattedDate} <i> ({daysDifference} days ago)</i>
          </span>
          )}
        </div>
      </div>
    </div>
  )
}

export default TeamMember
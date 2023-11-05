import { useState, useEffect } from "react"
import UserApi from "../api"
import Spinner from "./Spinner"
import { Button, Icon, Header } from "semantic-ui-react"

//Modal shows tips for a single task, using task id
function AiTipsModal({ task, closeModal }) {
  const [tips, setTips] = useState([])
  const [isLoading, setIsLoading] = useState(true)
  useEffect(
    function getTipsForTask() { 
      let controller = new AbortController()
      async function getTips() {    
        try {
          let res = await UserApi.getAiTips(task.id);
          console.log(res)
          setTips([...res.tips])
          setIsLoading(false);
          controller = null
        } catch (error) {
          console.error('Error fetching AI text:', error);
        }
      }
      getTips()
      return () => controller?.abort()
    }, [task])

  return (
    <div className="modal-background ">
      {isLoading ? <Spinner text='PriorityPilot is charting a course to help navigate this task...' /> :
      <div className="modal-content">
        <Button className='close-window' icon
                onClick={closeModal}
                size="tiny">
          <Icon name="close"></Icon>
        </Button>
        <Header>Here are some tips to navigate "{task.task_name}"!</Header>
        <ul>{tips.map(tip => (
          <li style={{ textAlign: 'left' }}>{tip}</li>))}
        </ul>
      </div>}
    </div>  
  )
}

export default AiTipsModal
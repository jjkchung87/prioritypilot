import { useContext, useState } from "react";
import { Form, Icon, Button } from "semantic-ui-react";
import DatePicker from 'react-datepicker'
import { ProjectsContext } from "../context/ProjectContext";

function EditTaskForm({ task, setShowForm, addUpdates, tasks }) {
    const { projects } = useContext(ProjectsContext)

    const initialState = {
      project_id: task.project_id,
      task_name: task.task_name,
      description: task.description,
      end_date:'',
      priority: task.priority,
      user_id: task.user_id,
      status: task.status,
      id: task.id
    }
    const [formData, setFormData] = useState(initialState)
    const past = (date) => new Date() < date;

    console.log('editedFormDtat', formData)
    console.log('tasks', tasks)
    
    const handleInputChange = (e) => {
      //saving data for date picker
      if (!e.target) {
        setFormData(data => ({
          ...formData, 
          end_date: e
        }))
      } else {
        const { name, value } = e.target
        setFormData(data => ({
          ...formData, 
          [name]: value
        })) 
      }
   }
   //handles edit form submit
   const saveUpdates = async (e) => {
    e.preventDefault()
    addUpdates(formData)
    setShowForm(false)
   }
   return (
    <div className="edit-task">
      <Form onSubmit={saveUpdates} className='edit-task-form'>
        <Button className='close-project-form' icon 
                onClick={()=>setShowForm(false)} size="tiny">
          <Icon name="close"></Icon>
        </Button>
        <h3>Edit Task</h3>
        <h4 className="project-name">{projects.filter(p => p.id === task.project_id)[0].project_name}</h4>
        <Form.Field>
          <label>Task Title</label>
          <input required className="task-name" name='task_name' value={formData.task_name} onChange={handleInputChange}/>  
        </Form.Field>
        <Form.Group inline >
          <label>Priority: </label>
          <Form.Field>
          Low <input name='priority' type="radio" value="Low" checked={formData.priority === 'Low'} onChange={handleInputChange}/>
          </Form.Field>
          <Form.Field>
          Medium <input name='priority' type="radio" value="Medium" checked={formData.priority === 'Medium'} onChange={handleInputChange}/>
          </Form.Field>
          <Form.Field>
          High <input name='priority' type="radio" value="High" checked={formData.priority === 'High'} onChange={handleInputChange}/>
          </Form.Field>
          <label>Deadline:</label>
          <DatePicker name='end_date' showTimeSelect filterDate={past} value={formData.end_date} selected={formData.end_date} onChange={handleInputChange} /> 
        </Form.Group>
        <Form.TextArea required label='Description' name="description" onChange={handleInputChange} value={formData.description}/>
        <Button fluid type='submit'>Save Updates</Button>
      </Form >
    </div>
  )
}
  
export default EditTaskForm
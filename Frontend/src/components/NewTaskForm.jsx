import { Form,Button, Header } from 'semantic-ui-react'
import { useContext, useState } from 'react'
import DatePicker from 'react-datepicker'
import 'react-datepicker/dist/react-datepicker.css'
import { UserContext } from '../context/UserContext'
import { ProjectContext, ProjectsContext } from '../context/ProjectContext'
import UserApi from '../api'
import {v4 as uuid} from 'uuid';


function NewTaskForm() {
  
  const { currentUser } = useContext(UserContext)
  const { currentProject, setCurrentProject } = useContext(ProjectContext)
  const { projects, setProjects } = useContext(ProjectsContext)

  let initialProject = currentProject ? currentProject.project_name : 'Select Project' 
  const initialState = {
    project: initialProject,
    title: '',
    description: '',
    deadline: '',
    priority: 'Low'
  }

  const [formData, setFormData] = useState(initialState)
  const [saved, setSaved] = useState(false)
  const past = (date) => new Date() < date;

  const handleInputChange = (e) => {
    //saving data for date picker
    if (!e.target) {
      setFormData(data => ({
        ...formData, 
        deadline: e
      }))
    } else {
      const { name, value } = e.target
      setFormData(data => ({
        ...formData, 
        [name]: value
      }))
      if (name === 'project') {
        let current = projects.filter(p => p.project_name === value)[0]
        setCurrentProject(current)
      }
    }
  }

 const saveNewTask = async(e) => {
   e.preventDefault()
   let data = {...formData, user_id: currentUser.id}
   let res = await UserApi.addTask(data, currentProject.id)
   setFormData(initialState)
   setCurrentProject(p => ({...p, tasks: [...p.tasks, res.task]}))
   setSaved(true)
 }
 console.log(formData)
 return (
    <>
    {!saved ?
    <Form onSubmit={saveNewTask} className='add-new-task'>
      <h3>Add New Task</h3>
      <Form.Group widths={'equal'}>
        <Form.Field>
          <label>Project Title</label>
          <select onChange={handleInputChange}  name='project' className='select'>
            {!currentProject ? 
              <>
                <option value='Select Project'>Select Project</option>
                {projects && projects.map(p => <option key={uuid()} value={p.project_name}>{p.project_name}</option>)}
              </> :
              <>
                <option value={currentProject.project_name}>{currentProject.project_name}</option> 
                {projects.filter(p => p.project_name !== currentProject.project_name).map(p => <option key={uuid()} value={p.project_name}>{p.project_name}</option>)}
              </>}
          </select> 
        </Form.Field>
        <Form.Field>
          <label>Task Title</label>
          <input required placeholder="Title" name='title' value={formData.title} onChange={handleInputChange}/>  
        </Form.Field>
      </Form.Group>
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
        <DatePicker name='deadline' showTimeSelect filterDate={past} value={formData.deadline} selected={formData.deadline} onChange={handleInputChange} /> 
      </Form.Group>
      <Form.TextArea required label='Description' name="description" placeholder='Your task...' onChange={handleInputChange} value={formData.description}/>
      <Button fluid type='submit'>Save Task</Button>
    </Form >
    : <Form><Header>You've added a New Task</Header></Form> 
    }</>
)
}

export default NewTaskForm
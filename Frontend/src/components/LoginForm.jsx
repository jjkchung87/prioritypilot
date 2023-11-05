import { Form, Input, Button, Header } from 'semantic-ui-react'
import './Forms.css'
import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { useNavigate } from 'react-router-dom'
import { UserContext } from '../context/UserContext'
import { useContext } from 'react'

function LoginForm({ login }) {
  const { currentUser } = useContext(UserContext)
  const navigate = useNavigate()
  useEffect(()=> {
    if (currentUser) navigate('/my_projects')
  })
  
  const initialState = {
    email: "",
    password: ""
  }
  const [formData, setFormData] = useState(initialState)
  const [error, setError] = useState(false)
  
  const handleInputChange = (e) => {
    const { name, value } = e.target
    setFormData(data => ({
      ...formData, 
      [name]: value
    }))
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    const result = await login(formData)
    if (result.success) {
      navigate('/my_projects')
    } else {
      setError(true)
      setFormData(initialState)
    }
  }

  return (
    <div className="login">
      <div className='image-logo'>
        Some Image
      </div>
      <Form onSubmit={handleSubmit}>
        <Header className='form-header'>Priority Pilot</Header>
        <Form.Field
          required
          type='email'
          id='form-input-control-error-email'
          control={Input}
          label='Email'
          value={formData.email}
          onChange={handleInputChange}
          placeholder='joe@schmoe.com'
          name='email'/>
        <Form.Field
          required
          type='password'
          id='form-input-control-last-name'
          control={Input}
          label='Password'
          name="password"
          value={formData.password}
          onChange={handleInputChange}
          placeholder='Password'/>
          {error && <span className='error-msg'>Invalid credentials</span>}
        <Form.Field>
        <p className='form-side-note'>Don't have an account? <Link to="/register">Register</Link> here.</p>
        </Form.Field>
        <Button fluid type='submit'>Sign In</Button>
      </Form>
    </div>
  )
}

export default LoginForm
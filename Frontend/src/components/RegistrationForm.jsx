import { Form, Input, Button, Checkbox } from 'semantic-ui-react'
import './Forms.css'
import { useState, useContext, useEffect } from 'react'
import { Link } from 'react-router-dom'
import { useNavigate } from 'react-router-dom'
import { UserContext } from '../context/UserContext'

function RegistrationForm({ register }) {
  const { currentUser } = useContext(UserContext)
  const navigate = useNavigate()
  useEffect(()=> {
    if (currentUser) navigate('/my_projects')
  })
  
  const initialState = {
    first_name: "",
    last_name: "",
    department: "",
    role: "",
    email: "",
    password: "",
    confirm_password: ""
  }
  
  const [formData, setFormData] = useState(initialState)
  const [passwordsNotMatch, setPasswordsNotMatch] = useState(false)
  const [passwordLengthValid, setPasswordLengthValid] = useState(true); // State for password length validation
  
  const handleInputChange = (e) => {
    const { name, value } = e.target
    setFormData(data => ({
      ...formData, 
      [name]: value
    }))
  }

  const handlePasswordBlur = () => {
    // Check if the password meets the minimum length requirement
    if (formData.password.length >= 8) {
      setPasswordLengthValid(true);
    } else {
      setPasswordLengthValid(false);
    }
  };

  //Takes current data (if valid) and passes it to register function, navigates to homepage.
  const handleSubmit = async (e) => {
    e.preventDefault()
    //check passwords 
    if (formData.password !== formData.confirm_password) {
      setPasswordsNotMatch(true)
    } else {
      let result = await register(formData)
      if (result.success) {
        navigate('/my_projects')
      } else {
        setFormData(initialState)
      }
    }
    
    
  }
  return (
    <div className="register">
      <Form onSubmit={handleSubmit}>
       
        <Form.Group widths={'equal'}>
          <Form.Field
            required
            id='form-input-control-first-name'
            control={Input}
            label='First name'
            placeholder='First name'
            value={formData.first_name}
            onChange={handleInputChange}
            name="first_name"/>
          <Form.Field
            required
            id='form-input-control-department'
            control={Input}
            label='Department'
            placeholder='Your Department'
            value={formData.department}
            onChange={handleInputChange}
            name="department"/>
        </Form.Group>
        <Form.Group widths='equal'>
          <Form.Field
            required
            id='form-input-control-last-name'
            control={Input}
            label='Last name'
            placeholder='Last name'
            value={formData.last_name}
            onChange={handleInputChange}
            name="last_name"/>
          <Form.Field
            required
            id='form-input-control-role'
            control={Input}
            label='Role'
            placeholder='Role'
            value={formData.role}
            onChange={handleInputChange}
            name="role"/>
        </Form.Group>
        <Form.Group widths={'equal'}>
        <Form.Field
         required
          type='email'
          id='form-input-control-error-email'
          control={Input}
          label='Email'
          value={formData.email}
          onChange={handleInputChange}
          placeholder='joe@schmoe.com'
          name='email'
          />
        <Form.Field
          id='form-input-control-photo'
          control={Input}
          label='Photo URL'
          value={formData.url}
          onChange={handleInputChange}
          placeholder='https://images.unsplash.com/photo-1566275529824'
          name='url'
          />
        </Form.Group>
        <Form.Group widths={'equal'}>
        <Form.Field
          required
          type="password"
          id='form-input-control-password'
          control={Input}
          label='Create Password'
          name="password"
          value={formData.password}
          onChange={handleInputChange}
          minLength="8"
          placeholder='Password'
          onBlur={handlePasswordBlur} // Add onBlur event handler
          />
        <Form.Field
          required
          minLength="8"
          type="password"
          id='form-input-control-confirm-password'
          control={Input}
          label='Confirm Password'
          name="confirm_password"
          value={formData.confirm_password}
          onChange={handleInputChange}
          placeholder='Enter Password Again..'/>

        </Form.Group>  
        {!passwordLengthValid && (
          <span className="error-msg">Password must be at least 8 characters long!</span>
        )}
        {passwordsNotMatch && <span className='error-msg'>Entered passwords don't match!</span>}
        <Form.Group widths='equal'>
          <Form.Field>
            <Checkbox label='I agree to the Terms and Conditions' required /> 
          </Form.Field>  
          <Form.Field>
            <p className='form-side-note'>Already a member? <Link to="/">Sign in </Link>here.</p>
          </Form.Field>
        </Form.Group>
        <Button fluid type='submit'>Register</Button>
      </Form>
    </div>
  )
}

export default RegistrationForm


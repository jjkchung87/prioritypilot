import { Button, Image } from 'semantic-ui-react'
import { Link } from 'react-router-dom'
import NewProjectForm from './NewProjectForm'
import { useState, useContext } from 'react'
import { UserContext } from '../context/UserContext'
import NavLogo from '../assets/nav_logo_white.png'
import { Icon } from 'semantic-ui-react'


function MainNavbar({ logout }) {
  const { currentUser } = useContext(UserContext)
  const [showForm, setShowForm] = useState(false)

  return (
    <div className="main-navbar wrapper">
        <Link to={'/'} className='logo-link'>
          <img className="logo-image" src={NavLogo} alt="PriorityPilot_Big_Logo"/>
        </Link>
        {currentUser ? 
        <div className='registered'>
          <Button className="new-project-button primary" content="+ Add New Project" onClick={()=>setShowForm(true)}/>
          {/* <Icon name='bell' size="small"/> */}
          <div>{currentUser.first_name} {currentUser.last_name}</div>
          <Image src={currentUser.profile_img} size='tiny' circular />
          <Link to={'/'} onClick={logout} style={{color: 'white'}}>Logout <Icon name="sign-out alternate"/></Link>
        </div> : 
        <div className='not-registered'>
          <Link to="/register" style={{color: 'white'}}>Register</Link>
        </div> }
    
        {showForm && <NewProjectForm setShowForm={setShowForm}/>}
    </div>
  )
}

export default MainNavbar
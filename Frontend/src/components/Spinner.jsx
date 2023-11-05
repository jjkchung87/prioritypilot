import Logo from "../assets/pp_logo.png"
function Spinner({text}) {
  return (
    <div className='spinner'>
      <h1>{text}</h1>  
      <img src={Logo} alt="spinner"></img>
    </div>
 )
}

export default Spinner
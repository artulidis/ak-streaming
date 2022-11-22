import React, {useState, useContext} from 'react'
import GlobalContext from '../../global/GlobalContext'
import ErrorMessage from '../../components/Auth/ErrorMessage'

const LoginForm = () => {

  const { loginUser, error, isError } = useContext(GlobalContext)

  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')

  const userLogin = (e) => {
    loginUser(e, username, password)
  }

  return (
    <>
      {isError ? <ErrorMessage error={username && password ? error : "Empty Fields"}/> : null}
      <div>
          <label>username:</label>
          <input name='username' onChange={(e) => setUsername(e.target.value)}></input>
      </div>

      <div>
          <label>password:</label>
          <input type={'password'} name='password' onChange={(e) => setPassword(e.target.value)}></input>
      </div>
      <button onClick={(e) => userLogin(e)}>login</button>
    </>
  )
}

export default LoginForm

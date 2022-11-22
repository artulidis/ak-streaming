import React, { useState, useRef } from 'react'
import { useNavigate } from 'react-router-dom'
import LoginForm from '../components/Auth/LoginForm'
import RegisterForm from '../components/Auth/RegisterForm'
import styles from '../css/auth.module.css'

const AuthPage = () => {

    const loginButton = useRef()
    const registerButton = useRef()
    const container = useRef()
    const form = useRef()

    const navigate = useNavigate()

    const [activeForm, setActiveForm] = useState('loginForm')

    const focusForm = (ref) => {
       if(activeForm !== ref) {
        if(activeForm === 'loginForm') {
            loginButton.current.className = styles.dormant
            registerButton.current.className = styles.active
            container.current.style.height = '55vh';
            form.current.style.height = '70%';
            navigate('/register')
            setActiveForm('registerForm')
        } else {
            loginButton.current.className = styles.active
            registerButton.current.className = styles.dormant
            container.current.style.height = '40vh';
            form.current.style.height = '50%';
            navigate('/login')
            setActiveForm('loginForm')
        }
       }
    }

  return (
    <div className={styles.loginContainer} ref={container}>
      <div className={styles.actionButtons}>
        <h3 ref={loginButton} onClick={()=> focusForm('loginForm')}>Login</h3>
        <h3 ref={registerButton} onClick={()=> focusForm('registerForm')}>Register</h3>
      </div>

      <form className={styles.form} ref={form}>
        {activeForm === 'loginForm' ? <LoginForm/> : <RegisterForm/>}
      </form>
    </div>
  )
}

export default AuthPage

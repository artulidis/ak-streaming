import React, {useContext} from "react"
import styles from '../../../css/layout.module.css'
import GlobalContext from "../../../global/GlobalContext"
import { Link } from "react-router-dom"

const LoginButton = () => {

    const {setOpen} = useContext(GlobalContext)
  
    return (
      <Link to={'/login'} onClick={() => setOpen(false)} className={styles.menuItem}>
        <span>Login/Register</span>
      </Link>
    )
  }

export default LoginButton
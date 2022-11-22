import React, {useContext} from "react"
import styles from '../../../css/layout.module.css'
import GlobalContext from "../../../global/GlobalContext"

const LogoutButton = () => {

    const {logoutUser} = useContext(GlobalContext)

    const userLogout = () => {
      logoutUser()
    } 
  
      return (
        <div onClick={userLogout} className={styles.menuItem}>
          <span>Logout</span>
        </div>
      )
  }

export default LogoutButton
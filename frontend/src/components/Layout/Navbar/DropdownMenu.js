import React, { useContext } from "react"
import GlobalContext from "../../../global/GlobalContext"
import DropdownItem from "./DropdownItem"
import LogoutButton from "./LogoutButton"
import LoginButton from "./LoginButton"
import styles from '../../../css/layout.module.css'

export const DropdownMenu = () => {

    const { user } = useContext(GlobalContext)
  
    return (
      <div className={styles.dropdown}>
          <div className="menu">
            <DropdownItem linkTo={'/profile'} loginRequired={true}>My Profile</DropdownItem>
            {user ? <LogoutButton/> : <LoginButton/>}
          </div>
      </div>
    );
  }

export default DropdownMenu
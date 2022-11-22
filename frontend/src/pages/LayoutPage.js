import React, { useContext, useState } from 'react'
import styles from '../css/layout.module.css'
import Navbar from '../components/Layout/Navbar/Navbar'
import {ReactComponent as NotificationIcon} from '../icons/general/notification-icon.svg'
import { Outlet } from 'react-router-dom'
import Sidebar from '../components/Layout/Sidebar/Sidebar'
import Profile from '../components/Layout/Navbar/Profile'
import DropdownMenu from '../components/Layout/Navbar/DropdownMenu'
import SideBarMenu from '../components/Layout/Sidebar/SideBarMenu'
import SideBarSubscriptions from '../components/Layout/Sidebar/SideBarSubscriptions'
import SideBarTopics from '../components/Layout/Sidebar/SideBarTopics'
import GlobalContext from '../global/GlobalContext'
import ResponsiveMenu from '../components/Layout/Navbar/ResponsiveMenu'

const LayoutPage = () => {

  const { user, following } = useContext(GlobalContext)

  const [refs, setRefs] = useState([])

  return (
    <div>
    <Navbar>
        <h1>ak streaming</h1>

        <ResponsiveMenu refs={refs} setRefs={setRefs} />

        <NotificationIcon className={styles.notificationIcon}/>
        <Profile refs={refs}>
            <DropdownMenu />
        </Profile>
    </Navbar>

    

    <Sidebar>
      <h3>menu</h3>
      <SideBarMenu />
        <div className={styles.sideBarDivider}></div>

        { user && following.length !== 0 ?
          <>
              <h3 className={styles.subscriptionsHeader}>subscribtions</h3>
              <SideBarSubscriptions />
              <div className={styles.topicsDivider}></div>
          </> : null
        }

        <h3>topics</h3>
        <SideBarTopics />
    </Sidebar>

    <Outlet/>
    </div>
  )
}

export default LayoutPage

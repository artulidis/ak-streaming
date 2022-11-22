import React from 'react'
import styles from '../../../css/layout.module.css'
import { useNavigate } from 'react-router-dom'
import { ReactComponent as CompassIcon } from '../../../icons/sidebar/compass-icon.svg'
import { ReactComponent as WatchListIcon } from '../../../icons/sidebar/watchlist-icon.svg'
import { ReactComponent as ChannelIcon } from '../../../icons/sidebar/channel-icon.svg'
import { ReactComponent as ActivityIcon } from '../../../icons/sidebar/activity-icon.svg'
import { ReactComponent as LikedIcon } from '../../../icons/sidebar/like-icon.svg'

const SideBarMenu = () => {

  const navigate = useNavigate()

  return (
    <div className={styles.menuContainer}>
        <div className={styles.sideBarItem} onClick={() => navigate('/')}>
            <CompassIcon className={styles.sideBarIcon} />
            <h4 className={styles.sideBarHeader}>Discover</h4>
        </div>

        <div className={styles.sideBarItem} onClick={() => navigate('/profile')}>
            <ChannelIcon className={styles.sideBarIcon} />
            <h4 className={styles.sideBarHeader}>My Profile</h4>
        </div>
    </div>
  )
}

export default SideBarMenu

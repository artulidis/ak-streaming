import React from 'react'
import styles from '../../../css/layout.module.css'

const Sidebar = (props) => {
  return (
    <div className={styles.sideBar}>
        {props.children}
    </div>
  )
}

export default Sidebar

import React from 'react'
import styles from '../../css/main.module.css'

const MainHeader = ({setSearch}) => {
  return (
    <div className={styles.mainHeader}>
      <h1 className={styles.discoverHeader}>discover</h1>
      <input className={styles.discoverInput} onChange={(e) => setSearch(e.target.value)} type="text" />
    </div>
  )
}

export default MainHeader

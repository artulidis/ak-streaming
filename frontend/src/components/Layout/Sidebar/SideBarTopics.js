import axios from 'axios'
import React, {useEffect, useState, useContext} from 'react'
import styles from '../../../css/layout.module.css'
import GlobalContext from '../../../global/GlobalContext'

const SideBarTopics = () => {

  const { topics, setTopicFilter } = useContext(GlobalContext)

  return (
    <div className={styles.topicsContainer}>
    <h4 className={styles.topic} onClick={() => setTopicFilter(null)}>#{"All"}</h4>
    {
        topics.map((topic, index) => (
            <h4 key={index} className={styles.topic} onClick={() => setTopicFilter(topic?.name)}>#{topic?.name}</h4>
        ))
    }
    </div>
  )
}

export default SideBarTopics

import React from 'react'
import styles from '../../css/video.module.css'

const Chat = (props) => {
  return (
    <div className={styles.chatComponent}>
      {props.children}
    </div>
  )
}

export default Chat

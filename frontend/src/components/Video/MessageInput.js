import React, { useContext, useState } from 'react'
import { useParams } from 'react-router-dom'
import styles from '../../css/video.module.css'
import axios from 'axios'
import GlobalContext from '../../global/GlobalContext'
import PlaneIcon from '../../icons/general/plane.png'

const MessageInput = (props) => {

  const {id, username, name} = useParams()


  return (
    <form>
      <input className={styles.messageInput} value={props.input} placeholder='Leave a Message...' onChange={(e) => props.setInput(e.target.value)}></input>

      <div className={styles.sendMessage}>
        <label>
          <img src={PlaneIcon} onClick={(e) => props.handleSubmit(e)} className={styles.planeIcon} />
        </label>
        <button type="submit" onClick={(e) => props.handleSubmit(e)}></button>
      </div>
    </form>
  )
}

export default MessageInput

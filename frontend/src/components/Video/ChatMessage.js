import React, { useContext, useEffect, useState } from 'react'
import styles from '../../css/video.module.css'
import GlobalContext from '../../global/GlobalContext'
import { useAxios } from '../../global/Axios'
import TimeAgo from 'javascript-time-ago'
import ReactTimeAgo from 'react-time-ago'
import en from 'javascript-time-ago/locale/en.json'

const ChatMessage = (props) => {

    const api = useAxios()
    const [profileImage, setProfileImage] = useState('')

    useEffect(() => {
      getProfileImage(props.message.user)
    },[])

    const getProfileImage = async (username) => {
      let user = await api.get(`http://127.0.0.1/api/user/${username}`)
      setProfileImage(user.data.profile_image)
    }


  return (
    <div className={styles.chatMessage}>
      <div className={styles.messageImage}>
        <img src={profileImage} alt='profile' className={styles.messageAvatar} />
        <p className={styles.messageText}>{props.message?.body}</p>
      </div>
      <div className={styles.timeAgo}>{<ReactTimeAgo date={Date.parse(props.message?.created)} locale="en-US" />}</div>
    </div>
  )
}

export default ChatMessage

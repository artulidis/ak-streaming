import React, { useContext } from 'react'
import styles from '../../css/profile.module.css'
import GlobalContext from '../../global/GlobalContext'
import { Link } from 'react-router-dom'
import DeleteIcon from '../../icons/general/delete-icon.png'
import EditIcon from '../../icons/general/edit-icon.png'
import { api } from '../../global/Axios'
import axios from 'axios'

const ContentEditButtons = ({post}) => {

    const { setProfileContent, user } = useContext(GlobalContext)

    const handleContentDelete = async () => {
        await axios.delete(`http://127.0.0.1/api/video/${post?.id}/`)
        
        let videos = await api.get(`api/videos/${user.user_id}`)
        setProfileContent(videos.data)
    }

  return (
    <div className={styles.contentEditButtons}>
        <img src={DeleteIcon} className={styles.deleteIcon} onClick={() => {handleContentDelete()}} />
    </div>
  )
}

export default ContentEditButtons
import React, {useEffect, useContext, useState} from 'react'
import { useParams } from 'react-router-dom'
import styles from '../../css/profile.module.css'
import { useAxios } from '../../global/Axios'
import GlobalContext from '../../global/GlobalContext'
import ContentItem from './ContentItem'
import {ReactComponent as AddContent} from '../../icons/general/addContent.svg'
import AddContentPopup from './AddContentPopup'

const ProfileContent = (props) => {

    const [isAdding, setIsAdding] = useState(false)

    const {profileContent, topicFilter, isEdit} = useContext(GlobalContext)

  return (
    <>
    { isAdding ? <AddContentPopup setIsAdding={setIsAdding} /> : null}
    <div className={styles.profileContent}>
      { props.username === undefined && !isEdit ? <div className={styles.addButton}><AddContent onClick={() => setIsAdding(true)} /></div> : null }
        {
            profileContent?.sort((a,b)=> a.created < b.created).map((post, index) => topicFilter !== null ? post?.topics.map((postTopic) => postTopic.name === topicFilter ? <ContentItem post={post} key={index} /> : null) : <ContentItem post={post} key={index} />)
        }
    </div>
    </>
  )
}

export default ProfileContent

import React from 'react'
import styles from '../../css/main.module.css'
import ContentItem from '../../components/Profile/ContentItem'

const VideoCategory = ({videos, topic}) => {

  return (
    <div className={styles.videoCategory}>
        <h3 className={styles.categoryHeader}>{topic.name}</h3>
        <div className={styles.videosContainer}>
            {
            videos.map((video) => video.topics.map((vidTopic) => vidTopic.name === topic.name ? <ContentItem post={video} mainPage={true}/> : null))
            }
        </div>
    </div>
  )
}

export default VideoCategory

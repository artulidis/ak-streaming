import React from 'react'
import styles from '../../css/video.module.css'

const VideoInfo = (props) => {
  return (
    <div className={styles.videoInfoContainer}>
      {props.children}
    </div>
  )
}

export default VideoInfo

import React from 'react'
import styles from '../../css/video.module.css'

const VideoJSLoading = () => {
  return (
    <div className={styles.videoJsLoading}>
      <div className={styles.ldsSpinner}><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div></div>
    </div>
  )
}

export default VideoJSLoading

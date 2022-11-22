import React, { useState, useContext, useEffect, useRef } from 'react'
import videojs from 'video.js';
import "video.js/dist/video-js.css";
import styles from '../../css/video.module.css'
import '../../css/videojs.scss'
import '@videojs/themes/dist/sea/index.css';
import "videojs-contrib-quality-levels";
import "videojs-http-source-selector";
import GlobalContext from '../../global/GlobalContext';

export const VideoJS = ({streamUrl, contentType}) => {

  // const [vodUrl, setVodUrl] = useState("")

  const player = useRef()
  const demo = useRef()

  const { user } = useContext(GlobalContext)

  console.log(streamUrl, contentType)

  // let streamUrl = `http://${task_ip}:8080/hls/${streamKey}.m3u8`
  // let streamUrl = `http://127.0.0.1/stream/rec/${streamKey}.mp4`

  const options = {
    muted: false,
    language: "en",
    preload: "auto",
  };

  useEffect(() => {
    const video = videojs(player.current, options, () => {
      demo.current.style.opacity = "1";
      console.log(player.current)
    });
    video.httpSourceSelector();
  },[])

  return (
    <div ref={demo} className={styles.demo}>
      <video
          ref={player}
          id="player"
          className={`${styles.videoJS} video-js vjs-theme-sea`} 
          controls
          playsInline
          preload="auto"
          data-setup="{}"
        >
          <source
            src={streamUrl}
            type={contentType}
            // type='application/x-mpegURL'
            // type='video/mp4'
        />
        </video>
    </div>
  );
}

export default VideoJS;

import React, {useState, useEffect, useRef} from 'react'
import styles from '../../css/profile.module.css'
import {ReactComponent as CloseIcon} from '../../icons/general/close-icon.svg'
import AddContentForm from './AddContentForm'

export function useUserMedia(requestedMedia) {
    const [mediaStream, setMediaStream] = useState(null)
  
    useEffect(() => {
      async function enableStream() {
        try {
          const stream = await navigator.mediaDevices.getUserMedia(requestedMedia)
          setMediaStream(stream)
        } catch(err) {
          console.log(err)
        }
      }
  
      if (!mediaStream) {
        enableStream()
      } else {
        return function cleanup() {
          mediaStream.getTracks().forEach(track => {
            track.stop()
          });
        }
      }
    }, [mediaStream, requestedMedia])
  
    return mediaStream;
  }


const AddContentPopup = (props) => {

    const video = useRef()
    const videoLoading = useRef()

    const options = {
        audio: false,
        video: true
    };

    const mediaStream = useUserMedia(options)

    if(mediaStream) {
        video.current.srcObject = mediaStream
    }

    const handleCanPlay = () => {
        video.current.play()
        videoLoading.current.style.display = 'none'
    }
    


    return (
        <div className={styles.addContentPopup}>
            <div className={styles.popupTop}>
              <CloseIcon onClick={() => props.setIsAdding(false)} />
            </div>
            <video ref={video} onCanPlay={() => handleCanPlay()} className={styles.popupVideo} playsInline muted ></video>
            <div className={styles.popupLoading} ref={videoLoading}>
            <p>(loading video preview)</p>
            <div className={styles.ldsSpinner}><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div><div></div></div>
            </div>

            <AddContentForm />
          </div>
    )
}

export default AddContentPopup

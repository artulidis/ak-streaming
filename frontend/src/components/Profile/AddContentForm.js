import React, { useState, useEffect, useRef, useContext } from 'react'
import { useNavigate } from 'react-router-dom'
import GlobalContext from '../../global/GlobalContext'
import axios from 'axios'
import styles from '../../css/profile.module.css'
import DropDown from '../../icons/general/dropdown.png'
import { ReactComponent as PlusIcon } from '../../icons/general/plus-icon.svg'
import { useAxios } from '../../global/Axios'
import { v4 as uuidv4 } from 'uuid';

const AddContentForm = () => {

    const { user, topics, profileContent, setProfileContent, ffmpegCommand, setFfmpegCommand } = useContext(GlobalContext)

    const api = useAxios()
    const navigate = useNavigate()

    const [title, setTitle] = useState("")
    const [checkedTopics, setCheckedTopics] = useState([])
    const [thumbnail, set_thumbnail] = useState([])
    const [streamKey, setStreamKey] = useState('')
    const [duration, setDuration] = useState(0)
    const [description, setDescription] = useState("")

    const [resolution, setResolution] = useState("1280x720")
    const [frameRate, setFrameRate] = useState(30)
    const [bitRate, setBitRate] = useState(1500)

    const [isImageSelected, setIsImageSelected] = useState(false)
    const [imageSelected, setImageSelected] = useState('')

    const [isDropDown, setIsDropDown] = useState(false)
    const [isResolutionDropDown, setIsResolutionDropDown] = useState(false)

    const setupTopicList = useRef("setupTopicList")
    const dropdownIcon = useRef("dropdownIcon")
    const resolutionDropdownIcon = useRef("resolutionDropdownIcon")
    const resolutionDropDownList = useRef("resolutionDropDownList")
    const resolutionHeader = useRef("resolutionHeader")

    let resolutions = ["1920x1080", "1280x720", "640x480", "256x144"]

    useEffect(() => {
        let _streamKey = `${user.username}-${uuidv4()}`
        setStreamKey(_streamKey)
    },[])

    const sendVideoSettings = async () => {
        
        let new_video = await axios.post("http://127.0.0.1/api/videos/post/topic/", {
            user: user.username,
            name: title,
            description: description,
            views: 0,
            thumbnail: null,
            stream_key: streamKey,
            likes: [],
            dislikes: [],
            topics: checkedTopics
        })

        await axios.putForm(`http://127.0.0.1/api/video/thumbnail/${new_video.data.id}/`, {
            thumbnail: thumbnail
        })

        let full_video = await axios.get(`http://127.0.0.1/api/video/${new_video.data.id}`)
        setProfileContent([...profileContent, full_video.data])

        return new_video.data.id

    }

    const createFfmpegCommand = async () => {
        const streamDuration = duration * 1
        let FfmpegCommand = `ffmpeg -f video4linux2 -i /dev/video0 -vcodec libx264 -preset ultrafast -t ${streamDuration} -pix_fmt yuv420p -s ${resolution} -r ${frameRate} -b:v ${bitRate}k -maxrate 7000k -c:a aac -b:a 128k -ac 2 -ar 44100 -f flv rtmp://127.0.0.1:1935/live/${streamKey}`

        if(ffmpegCommand == null) {
            localStorage.setItem('ffmpegCommandStorage', JSON.stringify(FfmpegCommand))
        } else {
            localStorage.removeItem('ffmpegCommandStorage')
            localStorage.setItem('ffmpegCommandStorage', JSON.stringify(FfmpegCommand))
        }

        setFfmpegCommand(FfmpegCommand)
    }

    const handleSubmit = async () => {
        let id = await sendVideoSettings()
        console.log(id)
        createFfmpegCommand()
        navigate(`/videos/${user.username}/${id}/live`)
    }

    const handleCheck = (e) => {
        e.target.previousSibling.checked = !e.target.previousSibling.checked
        setCheckedTopics(!e.target.previousSibling.checked ? checkedTopics.filter((topic) => topic !== parseInt(e.target.previousSibling.value)) : [...checkedTopics, parseInt(e.target.previousSibling.value)])
      }

    const handleResolutionCheck = (e) => {
        e.target.previousSibling.checked = !e.target.previousSibling.checked
        setResolution(e.target.innerHTML)
        resolutionHeader.current.innerText = e.target.innerText
    }

    const handleDropdown = () => {
        if(isDropDown) {
            setupTopicList.current.style.height = "8vh"
            setupTopicList.current.style.opacity = "1"

            dropdownIcon.current.style.transform = "rotate(180deg)"
            setIsDropDown(!isDropDown)
        } 
        else {
            dropdownIcon.current.style.transform = "rotate(0deg)"

            setupTopicList.current.style.opacity = "0"
            setupTopicList.current.style.height = "0vh"
            setIsDropDown(!isDropDown)
        }
    }

    const handleResolutionDropdown = () => {
        if(isResolutionDropDown) {
            resolutionDropDownList.current.style.height = "9vh"
            resolutionDropDownList.current.style.opacity = "1"
            resolutionDropDownList.current.style.pointerEvents = "all"

            resolutionDropdownIcon.current.style.transform = "rotate(180deg)"
            setIsResolutionDropDown(!isResolutionDropDown)
        } 
        else {
            resolutionDropdownIcon.current.style.transform = "rotate(0deg)"

            resolutionDropDownList.current.style.pointerEvents = "none"
            resolutionDropDownList.current.style.opacity = "0"
            resolutionDropDownList.current.style.height = "0vh"
            setIsResolutionDropDown(!isResolutionDropDown)
        }
    }

    const handleImageUpload = (e) => {
        if(e.target.files[0]) {
          let reader = new FileReader()
    
          reader.onload = (reader) => {
            setImageSelected(reader.target.result)
          }
          set_thumbnail(e.target.files[0])
          reader.readAsDataURL(e.target.files[0])
          setIsImageSelected(true)
        }
      }



  return (  
    
    <>
    <div className={styles.basicSetup}>
        <div className={styles.setupItem}>
            <label className={styles.setupLabel}>title:</label>
            <input className={styles.setupInput} onChange={(e) => {setTitle(e.target.value)}}></input>
        </div>

        <div className={styles.topicSetupItem}>
            <label className={styles.setupLabel}>topics:</label>
            <div className={styles.dropDownContainer}>
                <div className={styles.setupDropdown} onClick={() => handleDropdown()}>
                    <img src={DropDown} className={styles.dropdownIcon} ref={dropdownIcon} />
                    <h3>{"select video topic(s)..."}</h3>
                </div>

                <div className={styles.setupTopicList} ref={setupTopicList}>
                {
                topics?.map((topic, index) => (
                    <div className={styles.topicContainer} onClick={(e) => handleCheck(e)}>
                        <input type="checkbox" value={topic?.id} />
                        <h4 key={index} className={styles.topic}>{topic?.name}</h4>
                    </div>
                ))
                }
                </div>
            </div>
        </div>


        <div className={styles.thumbnailDurationContainer}>
            <div className={styles.thumbnailSetupItem}>
                <label className={styles.thumbnailImageLabel} htmlFor={'image-input'}>
                thumbnail:
                <div className={styles.thumbnailSetupContainer}>
                    {isImageSelected ? <img src={imageSelected} alt='selected' className={styles.thumbnailImageFile} /> : <PlusIcon className={styles.thumbnailAddIcon } />}
                </div>
                </label>
                <input name={'thumbnail'} id='image-input' type='file' accept='image/*' onChange={(e) => handleImageUpload(e)}></input>
            </div>
        
            <div className={styles.durationSetupItem}>
                <label className={styles.setupLabel}>duration:</label>
                <input className={styles.setupInput} type="number" value={duration} min="0" onChange={(e) => {setDuration(e.target.value)}}></input><span>mins</span>
            </div>
        </div>

        <div className={styles.descriptionSetupItem}>
            <label className={styles.setupLabel}>description:</label>
            <textarea className={styles.setupInput} onChange={(e) => {setDescription(e.target.value)}}></textarea>
        </div>
    </div>

    <div className={styles.advancedSetup}>
        <div className={styles.resolutionSetup}>
            <label className={styles.setupLabel}>resolution:</label>
            <div className={styles.resolutionDropDownContainer}>
                <div className={styles.resolutionDropDown} onClick={() => handleResolutionDropdown()}>
                    <p ref={resolutionHeader}>select resolution...</p>
                    <img src={DropDown} className={styles.resolutionDropdownIcon} ref={resolutionDropdownIcon} />
                </div>
                <div className={styles.resolutionDropDownList} ref={resolutionDropDownList}>
                    {
                        resolutions?.map((option, index)=> (
                            <div className={styles.resolutionOption} onClick={(e) => {handleResolutionCheck(e)}}>
                                <input type="radio" name='resolution'/>
                                <p>{option}</p>
                            </div>
                        ))
                    }
                </div>
            </div>
        </div>

        <div className={styles.frameRateSetup}>
            <label className={styles.frameRateLabel}>frame rate:</label>
            <input className={styles.frameRateInput} type="number" value={frameRate} min={24} max={60} onChange={(e) => {setFrameRate(e.target.value)}}></input>
        </div>

        <div className={styles.bitRateSetup}>
            <label className={styles.bitRateLabel}>video bitrate:</label>
            <input className={styles.bitRateInput} type="number" value={bitRate} min={1000} max={2500} onChange={(e) => {setBitRate(e.target.value)}}></input>
        </div>

    </div>

    <button className={styles.startStreamButton} onClick={() => handleSubmit()}>
        <h4>start stream</h4>
    </button>
    </>
    
  )
}

export default AddContentForm

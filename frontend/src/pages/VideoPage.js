import React, { useEffect, useState, useContext, useRef, useMemo } from 'react'
import styles from '../css/video.module.css'
import GlobalContext from '../global/GlobalContext'
import Chat from '../components/Video/Chat'
import MessageInput from '../components/Video/MessageInput'
import ChatMessage from '../components/Video/ChatMessage'
import axios from 'axios'
import { useLocation, useParams } from 'react-router-dom'
import { ReactComponent as LikeButton } from '../icons/general/like-video.svg'
import { ReactComponent as LikeButtonFilled } from '../icons/general/like-video-fill.svg'
import ReconnectingWebSocket from 'reconnecting-websocket';
import VideoJS from '../components/Video/VideoJS'
import VideoInfo from '../components/Video/VideoInfo'
import VideoJSLoading from '../components/Video/VideoJSLoading'

const VideoPage = () => {

  const [post, setPost] = useState(null)

  const [messages, setMessages] = useState([])
  const [input, setInput] = useState('')
  const [isFollowing, setIsFollowing] = useState(false)
  const [videoUser, setVideoUser] = useState('')
  const { user, thumbnail, following, setFollowing, ffmpegCommand } = useContext(GlobalContext)
  const [isLiked, setIsLiked] = useState('none')

  const [streamUrl, setStreamUrl] = useState(null)
  const [contentType, setContentType] = useState(null)

  const [isLive, setIsLive] = useState(window.location.href.includes("live"))
  const [task_ip, set_task_ip] = useState(null)
  const [isVideoJsAllowed, setIsVideoJsAllowed] = useState(window.location.href.includes("live") ? false : true)
  const {id} = useParams()

  let endpoint = `ws://127.0.0.1/ws/videos/${user.username}/${id}/`
  let socket = new ReconnectingWebSocket(endpoint)

  useEffect(() => {
   socket.onopen = (e) => {
      console.log("open", e)
   }
  },[])

  useEffect(() => {
    getVideoUser()
  },[])

  useEffect(() => {
    if(isLive) {
      startStream()
    }
  },[])

  useEffect(() => {
    createVideoUrls()
  },[task_ip])


  const createVideoUrls = async () => {
    let info = await getVideo()
    if(isLive && task_ip !== null) {
      setStreamUrl(`http://${task_ip}:8080/hls/${info.data.stream_key}.m3u8`)
      setContentType('application/x-mpegURL')
    } else {
      setStreamUrl(`http://127.0.0.1/stream/rec/${info.data.stream_key}.mp4`)
      setContentType('video/mp4')
    }
  } 

  const handleSubmit = (e) => {
    e.preventDefault()
    socket.send(JSON.stringify({
      user: user.username,
      body: input,
      video: id
    }))
  }

  socket.onmessage = (e) => {
    let message_data = JSON.parse(e.data)
    setMessages([...messages, message_data])
    setInput('')
 }

  useEffect(() => {
    if(following.includes(videoUser?.id)) {
      setIsFollowing(true)
    }
  },[videoUser])

  const getVideo = async () => {
    let postInfo = await axios.get(`http://127.0.0.1/api/video/${id}`)
    setPost(postInfo.data)
    postInfo.data.likes.includes(user.user_id) || postInfo.data.dislikes.includes(user.user_id) ? postInfo.data.likes.includes(user.user_id) ? setIsLiked(true) : setIsLiked(false) : setIsLiked('none')
    return postInfo
  }

  const getVideoUser = async () => {
    try {
      let video = await getVideo()
      let user = await axios.get(`http://127.0.0.1/api/user/${video.data.user}`)
      setVideoUser(user.data)
    } catch(err) {
      console.log(err)
    }
  }

  useEffect(() => {
    getComments()
  },[messages.length])

  const getComments = async () => {
    try {
      let comments = await axios.get(`http://127.0.0.1/api/comments/${id}`)
      setMessages(comments.data)
    } catch(err) {
      console.log(err)
    }
  }

  const handleFollow = async (e) => {

    e.preventDefault()
    await axios.put(`http://127.0.0.1/api/following/${user.user_id}/`, {
      owner: user.username,
      users: !isFollowing ? [...following, videoUser?.id] : following.filter(user_id => user_id !== videoUser?.id)
    })

    await axios.put(`http://127.0.0.1/api/followers/${videoUser?.username}/`, {
      username: videoUser?.username,
      followers: !isFollowing ? parseInt(videoUser?.followers + 1) : parseInt(videoUser?.followers - 1)
    })

    getVideoUser()
    console.log(videoUser?.followers)

    setIsFollowing(!isFollowing)
    setFollowing(!isFollowing ? [...following, videoUser?.id] : following.filter(user_id => user_id !== videoUser?.id))

  }

  const handleLike = async (action) => {
    let response = await axios.put(`http://127.0.0.1/api/video/likes/${id}/`, {
      likes: action === 'like' ? isLiked === true ? post?.likes.filter(liked_user => user.user_id !== liked_user) : [...post?.likes, user.user_id] : isLiked === true ? post?.likes.filter(liked_user => user.user_id !== liked_user) : post?.likes,
      dislikes: action === 'like' ? isLiked === false ? post?.dislikes.filter(disliked_user => user.user_id !== disliked_user) : post?.dislikes : isLiked === false ? post?.dislikes.filter(disliked_user => user.user_id !== disliked_user) : [...post?.dislikes, user.user_id],
    })

    console.log(response)
    getVideo()
  }

  const startStream = () => {
    setTimeout(async () => {
      let task_info = await axios.post('http://127.0.0.1/rtmp/start/', {
        ffmpegCommand: ffmpegCommand
      })
      set_task_ip(task_info?.data.ip)
      setTimeout(() => setIsVideoJsAllowed(true), 1000)
    },1000)
  }

  return (
    <div>
      <div className={styles.videoContainer}>
        { isVideoJsAllowed && streamUrl !== null && contentType !== null ? <VideoJS streamUrl={streamUrl} contentType={contentType} /> : <VideoJSLoading /> }
        {/* {task_ip !== null && isVideoJsAllowed ? <VideoJS task_ip={task_ip} streamKey={post?.stream_key} isLive={isLive} /> : <VideoJSLoading /> } */}

        <VideoInfo>
          <div className={styles.userInfo}>
            <div className={styles.videoInfo}>
            <h5 className={styles.videoTitle}>{post?.name}</h5>
              <div className={styles.topics}>
              {
                post?.topics.map((topic, index)=> (<div key={index} className={styles.videoTopic}>{topic.name}</div>))
              }
              </div>
            </div>

            <div className={styles.videoActions}>
                <div className={styles.likeButtonContainer}>
                  {isLiked === true ? <LikeButtonFilled className={styles.likeButton} onClick={() => {handleLike('like')}} /> : <LikeButton className={styles.likeButton} onClick={() => {handleLike('like')}} />}
                  <h5 className={styles.likeStat}>{post?.likes.length}</h5>
                </div>

                <div className={styles.dislikeButtonContainer}>
                  {isLiked === false ? <LikeButtonFilled className={styles.dislikeButton} onClick={() => {handleLike('dislike')}} /> : <LikeButton className={styles.dislikeButton} onClick={() => {handleLike('dislike')}} />}
                  <h5 className={styles.likeStat}>{post?.dislikes.length}</h5>
                </div>
            </div>
          </div>
          

          <div className={styles.videoDescription}>
            <div className={styles.profileActions}>
              <div className={styles.userProfile}>
                <img src={videoUser?.profile_image} className={styles.infoProfileImage} />
                <div className={styles.infoNameFollowers}>
                  <h5 className={styles.infoUserName}>{videoUser?.full_name}</h5>
                  <p className={styles.infoFollowers}>{`${videoUser?.followers} ${videoUser?.followers === 1 ? 'follower' : 'followers'}`}</p>
                </div>
              </div>

              <div className={styles.userActions}>
              {videoUser?.username !== user.username ? <button className={!isFollowing ? styles.followProfile : styles.followProfileFollowed} onClick={(e)=> handleFollow(e)}>{!isFollowing ? 'Follow +' : 'Following'}</button> : null}
              </div>
            </div>

            <div className={styles.description}>
              <span>Description:</span>
              <p>{post?.description}</p>
            </div>
          </div>
        </VideoInfo>


        <div className={styles.responsiveChatContainer}>
          <Chat>
            <div className={styles.chatHeader}>stream chat</div>

            <div className={styles.messagesContainer}>
              {
                messages.sort((a,b)=> a.created < b.created).map((message, index) => (
                    <ChatMessage message={message} key={index} />
                ))
              }
            </div>
            <MessageInput handleSubmit={handleSubmit} input={input} setInput={setInput} />
          </Chat>
        </div>
      </div>

      <div className={styles.chatContainer}>
        <Chat>
          <div className={styles.chatHeader}>stream chat</div>

          <div className={styles.messagesContainer}>
            {
              messages.sort((a,b)=> a.created < b.created).map((message, index) => (
                  <ChatMessage message={message} key={index} />
              ))
            }
          </div>
          <MessageInput handleSubmit={handleSubmit} input={input} setInput={setInput} />
        </Chat>
      </div>
    </div>
  )
}

export default VideoPage
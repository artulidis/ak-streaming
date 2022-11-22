import axios from 'axios'
import React, { useContext, useEffect, useState } from 'react'
import { useParams } from 'react-router-dom'
import styles from '../../css/profile.module.css'
import { useAxios } from '../../global/Axios'
import GlobalContext from '../../global/GlobalContext'
import ProfileImage from './ProfileImage'

const ProfileInfo = (props) => {

  const { user, profile_image, profileContent, isEdit, setIsEdit, profileInfo, setFollowing, following } = useContext(GlobalContext)
  const api = useAxios()
  const id = profileInfo?.id
  console.log(id)

  const [other_following, set_other_following] = useState([])
  const [isFollowing, setIsFollowing] = useState(false)
  const [formData, setFormData] = useState({
    username: null,
    full_name: null,
    bio: null
  })

  useEffect(()=> {
    setFormData({
      username: profileInfo?.username,
      full_name: profileInfo?.full_name,
      bio: profileInfo?.bio
    })

    if(following.includes(profileInfo?.id)) {
      setIsFollowing(true)
    }

  },[profileInfo])

  useEffect(() => {
    if(profileInfo?.username !== user?.username) {
      getUserFollowing()
    }
  },[])

  const handleFollow = async (e) => {

    e.preventDefault()
    await axios.put(`http://127.0.0.1/api/following/${user.user_id}/`, {
      owner: user.username,
      users: !isFollowing ? [...following, profileInfo?.id] : following.filter(user_id => user_id !== profileInfo?.id)
    })

    await axios.put(`http://127.0.0.1/api/followers/${profileInfo?.username}/`, {
      username: profileInfo?.username,
      followers: !isFollowing ? parseInt(profileInfo?.followers + 1) : parseInt(profileInfo?.followers - 1)
    })

    props.getProfile()
    console.log(profileInfo?.followers)

    setIsFollowing(!isFollowing)
    setFollowing(!isFollowing ? [...following, profileInfo?.id] : following.filter(user_id => user_id !== profileInfo?.id))

  }

  const handleProfileEdit = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    })
  }

  const getUserFollowing = async () => {
    let followingList = await axios.get(`http://127.0.0.1/api/following/${id}`)
    set_other_following(followingList.data.users)
  }


  const handleSubmit = async (e) => {
    if(!isEdit) {
      setIsEdit(!isEdit)
    } else {
      e.preventDefault()
      let response = await api.putForm(`/api/user/${user.username}/`, {
        "username": formData.username,
        "password": profileInfo?.password,
        "email": profileInfo?.email,
        "full_name": formData.full_name,
        "profile_image": profile_image,
        "followers": profileInfo?.followers,
        "bio": formData.bio
      })
      if(response.status === 200) {
        props.getProfile()
        setIsEdit(!isEdit)
      }
    }
  }


  return (
    <>
      <ProfileImage />
      <div className={styles.profileInfo}>
          <div className={styles.profileInfoTop}>
              <h4 className={styles.usernameLabel}>{profileInfo?.username}</h4> 
              {profileInfo?.username === user?.username ? <button className={!isEdit ? styles.editProfile : styles.editProfileEdit} onClick={(e)=> handleSubmit(e)}>{!isEdit ? 'Edit Profile' : 'Apply'}</button> : <button className={!isFollowing ? styles.followProfile : styles.followProfileFollowed} onClick={(e)=> handleFollow(e)}>{!isFollowing ? 'Follow +' : 'Following'}</button>}
          </div>
          
          <div className={styles.statContainer}>
              <div><h4>{profileContent ? profileContent.length : 0}</h4><span>posts</span></div>
              <div><h4>{profileInfo?.followers}</h4><span>followers</span></div>
              <div><h4>{profileInfo?.username === user?.username ? following.length : other_following.length}</h4><span>following</span></div>
          </div>

          <div className={styles.bioContainer}>
              {!isEdit ? <h4 className={styles.fullName}>{`${profileInfo?.full_name} `}</h4> : <input name='full_name' value={formData.full_name} className={styles.fullNameEdit} onChange={(e)=> handleProfileEdit(e)}/>}
              {!isEdit ? <p className={styles.bio}>{profileInfo?.bio}</p> : <textarea name='bio' value={formData.bio} className={styles.bioEdit} onChange={(e)=> handleProfileEdit(e)} />}
          </div>
      </div>
    </>
  )
}

export default ProfileInfo

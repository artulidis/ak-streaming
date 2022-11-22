import React, { useContext, useEffect, } from 'react'
import { useAxios } from '../global/Axios'
import { useParams } from 'react-router-dom'
import ProfileContent from '../components/Profile/ProfileContent'
import ProfileInfo from '../components/Profile/ProfileInfo'
import GlobalContext from '../global/GlobalContext'


const ProfilePage = () => {

  const { user, profileInfo, setProfileInfo, setProfileContent } = useContext(GlobalContext)
  const params = useParams()
  const api = useAxios()
  
  useEffect(()=> {
    getProfile()
  },[params.username])

  const getProfile = async () => {
    try {
      let profile_info = await api.get(`/api/user/${params.username === undefined ? user.username : params.username}`)
      setProfileInfo(profile_info.data)

      let videos = await api.get(`api/videos/${params.username === undefined ? user.user_id : profile_info.data.id}`)
      console.log(videos.data)
      setProfileContent(videos.data)

    } catch(error) {
      console.log(error)
    }
  }

  return (
    <div>
        <ProfileInfo getProfile={getProfile} />

        <ProfileContent username={params.username === undefined ? undefined : profileInfo?.username} />
    </div>
  )
}

export default ProfilePage

import React, { useContext, useEffect, useState } from 'react'
import MainHeader from '../components/Main/MainHeader'
import styles from '../css/main.module.css'
import GlobalContext from '../global/GlobalContext'
import VideoCategory from '../components/Main/VideoCategory'
import SearchResults from '../components/Main/SearchResults'
import axios from 'axios'

const MainPage = () => {

  const { topics, topicFilter } = useContext(GlobalContext)

  const [videos, setVideos] = useState([])
  const [search, setSearch] = useState("")
  
  let isSearch = search === "" ? false : true

  useEffect(() => {
    getVideos()
  },[])

  const getVideos = async () => {
    let videos = await axios.get("http://127.0.0.1/api/videos/")
    setVideos(videos.data)
  }

  return (
    <div className={styles.mainPage}>
      <MainHeader setSearch={setSearch} />

      <div className={styles.categoryContainer}>
        {
          !isSearch ? topicFilter !== null ? topics?.filter((topic) => topic.name === topicFilter).map((topic) => <VideoCategory videos={videos} topic={topic} />) : topics?.map((topic) => <VideoCategory videos={videos} topic={topic}/>) : (
            <SearchResults videos={videos} search={search} />
          )
        }
      </div>

    </div>
  )
}

export default MainPage

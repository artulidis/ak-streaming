import React from 'react'
import styles from '../../css/main.module.css'
import ContentItem from '../Profile/ContentItem'

const SearchResults = ({videos, search}) => {
  return (
    <div className={styles.searchResultsContainer}>
        <h3 className={styles.categoryHeader}>Search Results:</h3>

        <div className={styles.videosContainer}>
            {
                videos.filter((video) => video.name.toLowerCase().includes(search.toLowerCase()) || video.user.toLowerCase().includes(search.toLowerCase()) || video.description.toLowerCase().includes(search.toLowerCase())).map((video) => (
                    <ContentItem post={video} mainPage={true} />
                ))
            }
        </div>
    </div>
  )
}

export default SearchResults

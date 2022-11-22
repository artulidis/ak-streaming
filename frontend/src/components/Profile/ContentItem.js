import TimeAgo from 'javascript-time-ago'
import ReactTimeAgo from 'react-time-ago'
import en from 'javascript-time-ago/locale/en.json'
import styles from '../../css/profile.module.css'
import { Link, useParams } from 'react-router-dom'
import { useContext, useState, useEffect } from 'react'
import GlobalContext from '../../global/GlobalContext'
import ContentEditButtons from './ContentEditButtons'
import axios from 'axios'


TimeAgo.addDefaultLocale(en)

const ContentItem = ({post, mainPage}) => {

    const { isEdit } = useContext(GlobalContext)

    const [avatar, setAvatar] = useState("")

    useEffect(() => {
        if(mainPage) {
            getAvatar()
            console.log(avatar)
        }
    },[])

    const getAvatar = async () => {
        let avatar = await axios.get(`http://127.0.0.1/api/user/profile_image/${post.user}/`)
        setAvatar(avatar.data.profile_image)
    }

    const handleViewCount = async (post) => {

        let thumbnail = await axios.get(post.thumbnail)

        await axios.putForm(`http://127.0.0.1/api/video/${post.id}/`, {
            user: post.user,
            name: post.name,
            description: post.description,
            views: post.views + 1,
            thumbnail: thumbnail
        })
    }

    return (
        <div className={styles.contentItemContainer}>
            {isEdit ? <ContentEditButtons post={post} /> : null}
            <Link to={`/videos/${post.user}/${post?.id}`} className={styles.contentItemLink} onClick={() => handleViewCount(post)}>
                <div className={styles.contentItem}>
                {mainPage ? <div className={styles.userAvatarContainer}><img src={avatar} className={styles.userAvatar} /></div> : null}
                    <img src={post?.thumbnail} alt='video-thumbnail' className={styles.videoThumbnail} />
                    
                    <p className={styles.videoTitle}>{post?.name}</p>
                    <h5 className={styles.views}>{post?.views} views • {<ReactTimeAgo date={Date.parse(post?.created)} locale="en-US" />}</h5>

                    <div className={styles.tags}>

                        {
                            post.topics?.map((topic, index) => (
                                <h5 key={index} className={styles.tag}>{topic.name}</h5>
                            ))
                        }

                    </div>
                </div>
            </Link>
        </div>
    )
}

export default ContentItem
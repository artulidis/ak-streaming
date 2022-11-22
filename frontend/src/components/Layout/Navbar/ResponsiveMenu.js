import React, {useContext, useState, useRef, useEffect} from 'react'
import styles from '../../../css/layout.module.css'
import SubscriptionItem from '../Sidebar/SubscriptionItem'
import GlobalContext from '../../../global/GlobalContext'
import { Link } from 'react-router-dom'

const ResponsiveMenu = ({refs, setRefs}) => {

    const { following, toggle, topics, setTopicFilter } = useContext(GlobalContext)

    const responsiveSubscriptions = useRef("responsiveSubscriptions")
    const responsiveTopics = useRef("responsiveTopics")

    useEffect(() => {
        setRefs([responsiveSubscriptions, responsiveTopics])
    },[responsiveSubscriptions, responsiveTopics])

    const handleTopicFilter = (topic, e) => {
        e.target.innerText === "All" ? setTopicFilter(null) : setTopicFilter(topic?.name)
        toggle(responsiveTopics, responsiveSubscriptions)
    }

  return (
    <div className={styles.responsiveMenu}>
        
        <Link to={"/"} className={styles.responsiveMenuLink}>
            <h4 className={styles.responsiveMenuHeading}>discover</h4>
        </Link>

        <Link to={"profile/"} className={styles.responsiveMenuLink}>
            <h4 className={styles.responsiveMenuHeading}>my profile</h4>
        </Link>

        <div className={styles.responsiveSubscriptionContainer}>
            <div className={styles.responsiveMenuHeadingContainer}>
                <h4 className={styles.responsiveMenuHeadingSubscription} onClick={() => toggle(responsiveSubscriptions, responsiveTopics)}>subscribtions</h4>
            </div>
            <div className={styles.responsiveSubscriptions} id={"subscriptions"} ref={responsiveSubscriptions}>
                {
                    following.map((subscription, index)=> (
                        <SubscriptionItem key={index} subscription={subscription} refs={refs} />
                    ))
                }
            </div>
        </div>
        
        <div className={styles.responsiveSubscriptionContainer}>
            <div className={styles.responsiveMenuHeadingContainer}>
                <h4 className={styles.responsiveMenuHeadingTopic} onClick={() => toggle(responsiveTopics, responsiveSubscriptions)}>topics</h4>
            </div>
            <div className={styles.responsiveTopics} id={"topics"} ref={responsiveTopics}>
                <div className={styles.topicsContainer}>
                    <h4 className={styles.topic} onClick={(e) => handleTopicFilter(null, e)}>{"All"}</h4>
                    {
                        topics.map((topic, index) => (
                            <h4 key={index} className={styles.topic} onClick={(e) => handleTopicFilter(topic, e)}>{topic?.name}</h4>
                        ))
                    }
                </div>
            </div>
            
        </div>
      
    </div>
  )
}

export default ResponsiveMenu

import axios from 'axios'
import React, { useContext, useEffect, useState } from 'react'
import styles from '../../../css/layout.module.css'
import { Link } from 'react-router-dom'
import GlobalContext from '../../../global/GlobalContext'

const SubscriptionItem = ({subscription, index, refs}) => {

    const { toggle } = useContext(GlobalContext)

    const [user, setUser] = useState(null)

    useEffect(() => {
        getUserProfile()
    },[])

    const getUserProfile = async () => {
        let response = await axios.get(`http://127.0.0.1/api/subscription/${subscription}`)
        setUser(response.data)
    }

  return (
    <Link to={`/profile/${user?.username}`} className={styles.subscriptionLink} onClick={() => refs !== undefined ? toggle(refs) : null}>
        <div key={index} className={styles.subscription}>
            <img src={user?.profile_image} className={styles.subscriptionProfilePicture}/>
            <h4>{user?.username}</h4>
        </div>
    </Link>
  )
}

export default SubscriptionItem

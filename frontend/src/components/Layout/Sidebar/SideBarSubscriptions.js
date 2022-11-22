import React, {useContext, useState} from 'react'
import styles from '../../../css/layout.module.css'
import GlobalContext from '../../../global/GlobalContext'
import SubscriptionItem from './SubscriptionItem'


const SideBarSubscriptions = () => {

  const { following } = useContext(GlobalContext)

  return (
    <div className={styles.subscriptionContainer}>
    {
        following.map((subscription, index)=> (
            <SubscriptionItem key={index} subscription={subscription} />
        ))
    }
    </div>
  )
}

export default SideBarSubscriptions

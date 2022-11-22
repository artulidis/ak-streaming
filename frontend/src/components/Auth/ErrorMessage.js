import React from 'react'
import styles from '../../css/auth.module.css'

const ErrorMessage = ({error}) => {

    let error_message = ''

    switch(error) {
        case "Unauthorized":
            error_message = "Either Username or Password is Incorrect"
            break

        case "Empty Fields":
            error_message = "Please Make Sure to Enter Credentials"
            break

        case "Invalid Username":
            error_message = "This Username is Taken"
            break
        
        case "Invalid Email":
            error_message = "Please Input a Valid Email Address"
            break

        default:
            error_message = "Error Authenticating User"
            break
    }

  return (
    <div className={styles.errorMessage}>
      <h5>{error_message}</h5>
    </div>
  )
}

export default ErrorMessage

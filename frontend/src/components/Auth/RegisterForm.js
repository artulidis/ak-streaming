import React, { useState, useContext } from 'react'
import styles from '../../css/auth.module.css'
import axios from 'axios'
import { ReactComponent as PlusIcon } from '../../icons/general/plus-icon.svg'
import GlobalContext from '../../global/GlobalContext'
import ErrorMessage from './ErrorMessage'

const RegisterForm = () => {

  const { loginUser, isError, setIsError, error, setError } = useContext(GlobalContext)

  const [isImageSelected, setIsImageSelected] = useState(false)
  const [imageSelected, setImageSelected] = useState('')
  const [profile_image, setProfile_Image] = useState(null)
  const [formData, setFormData] = useState({
    full_name: '',
    username: '',
    password: '',
    email: '',
    bio: ''
  })


  const handleFormChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    })
  }


  const handleImageUpload = (e) => {
    if(e.target.files[0]) {
      let reader = new FileReader()

      reader.onload = (reader) => {
        setImageSelected(reader.target.result)
      }
      setProfile_Image(e.target.files[0])
      reader.readAsDataURL(e.target.files[0])
      setIsImageSelected(true)
    }
  }


  const handleSubmit = async (e) => {
    try {
      e.preventDefault()
      await axios.postForm('http://127.0.0.1/api/users/', {
        "username": formData.username,
        "password": formData.password,
        "email": formData.email,
        "full_name": formData.full_name,
        "profile_image": profile_image,
        "followers": 0,
        "following": 0,
        "bio": formData.bio
      })
      loginUser(e, formData.username, formData.password)
    } catch(error) {
      if(!isError) {
        setIsError(true)
        let users = await axios.get('http://127.0.0.1/api/users/')
        users.data.forEach((user)=> {
          if(user.username === formData.username) {
            setError("Invalid Username")
          } else {
            setError("Invalid Email")
          }
        })

      }

      setTimeout(()=> {
        setIsError(false)
        setError(null)
      },2300)
    }

  }


  return (
    <div className={styles.registerFormContainer}>
      {isError ? <ErrorMessage error={error}/> : null}
      <div className={styles.registerTopForms}>
        <div>
            <label className={styles.registerLabel}>full name</label>
            <input className={styles.registerInput} name={'full_name'} value={formData.full_name} onChange={(e) => handleFormChange(e)}></input>
        </div>

        <div>
            <label className={styles.registerLabel}>username</label>
            <input className={styles.registerInput} name={'username'} value={formData.username} onChange={(e) => handleFormChange(e)}></input>
        </div>

        <div>
            <label className={styles.registerLabel}>password</label>
            <input className={styles.registerInput} name={'password'} value={formData.password} onChange={(e) => handleFormChange(e)} type={'password'}></input>
        </div>

        <div>
            <label className={styles.registerLabel}>email</label>
            <input className={styles.registerInput} name={'email'} value={formData.email} onChange={(e) => handleFormChange(e)}></input>
        </div>
      </div>

    <div className={styles.registerAddAvatar}>
        <label className={styles.registerImageLabel} htmlFor={'image-input'}>
        profile picture
        <div className={styles.registerAddIconContainer}>
          {isImageSelected ? <img src={imageSelected} alt='selected' className={styles.registerImageFile} /> : <PlusIcon className={styles.registerAddIcon } />}
        </div>
        </label>
        <input name={'profile_image'} id='image-input' type='file' accept='image/*' onChange={(e) => handleImageUpload(e)}></input>
    </div>

    <div className={styles.registerBio}>
        <label className={styles.registerLabel}>bio:</label>
        <textarea name={'bio'} value={formData.bio} onChange={(e) => handleFormChange(e)}></textarea>
        <button className={styles.registerButton} onClick={(e) => handleSubmit(e)}>Register</button>
    </div>
    </div>
  )
}

export default RegisterForm

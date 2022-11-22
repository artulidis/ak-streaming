import { useState, useContext } from "react"
import styles from '../../css/profile.module.css'
import GlobalContext from "../../global/GlobalContext"

const ProfileImage = () => {

    const [isImageSelected, setIsImageSelected] = useState(false)
    const [imageSelected, setImageSelected] = useState('')

    const { profileInfo, isEdit, setProfile_Image } = useContext(GlobalContext)

    const handleImageUpload = (e) => {
      if(e.target.files[0]) {
        let reader = new FileReader()
  
        reader.onload = (reader) => {
          setImageSelected(reader.target.result)
        }
        setProfile_Image(e.target.files[0])
        console.log(e.target.files[0])
        reader.readAsDataURL(e.target.files[0])
        setIsImageSelected(true)
      }
    }
  
    if(isEdit) {
      return (
        <div className={styles.registerAddAvatar}>
          <label className={styles.registerImageLabel} htmlFor={'image-input'}>
            {isImageSelected ? <img src={imageSelected} alt='selected' className={styles.profilPictureEdit} /> : <img src={profileInfo?.profile_image} alt='profile' className={!isEdit ? styles.profilePicture : styles.profilPictureEdit} />}
          </label>
          <input name={'profile_image'} id='image-input' type='file' accept='image/*' onChange={(e) => handleImageUpload(e)}></input>
        </div>
      )
    }
  
  return (
    <img src={profileInfo?.profile_image} alt='profile' className={!isEdit ? styles.profilePicture : styles.profilPictureEdit} />
  )
}

export default ProfileImage
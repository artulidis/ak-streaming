import React, {useContext} from "react"
import styles from '../../../css/layout.module.css'
import GlobalContext from "../../../global/GlobalContext";
import { Link } from "react-router-dom";

function DropdownItem(props) {

    const { open, setOpen, user } = useContext(GlobalContext)

    return (
        !user && props.loginRequired ? 
        null :
        <Link to={props.linkTo} className={styles.menuItem} onClick={()=> setOpen(!open)} >
          <span>{props.children}</span>
        </Link>
    );
  }

export default DropdownItem
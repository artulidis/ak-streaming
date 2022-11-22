import React, {useContext, useEffect, useState} from "react";
import styles from '../../../css/layout.module.css'

function Navbar(props) {
    return (
      <nav className={styles.navbar}>
        <ul>{props.children}</ul>
      </nav>
    );
  }
  
export default Navbar
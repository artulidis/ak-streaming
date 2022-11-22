import GlobalContext from "./GlobalContext"
import React, { useContext } from "react"
import { Navigate, Outlet } from "react-router-dom"

const useAuthenticated = () => {
    const { user } = useContext(GlobalContext)
    return user != null
}

const PrivateRoute = () => {

    const isAuthenticated = useAuthenticated()

    return (
        isAuthenticated ? <Outlet /> : <Navigate to={'/login'}/>
    )
}

export default PrivateRoute
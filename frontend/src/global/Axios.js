import axios from 'axios'
import { useContext } from 'react'
import GlobalContext from '../global/GlobalContext'
import jwt_decode from "jwt-decode"
import dayjs from 'dayjs'

const baseURL = 'http://127.0.0.1:8000/'

export const api = axios.create({
    baseURL,
    headers: {'Content-Type': 'application/json'}
  });


export const useAxios = () => {
    const {setUser, setAuthTokens, authTokens} = useContext(GlobalContext)

    const interceptorInstance = axios.create({
        baseURL,
        headers:{Authorization: `Bearer ${authTokens?.access}`}
    });
  
  
interceptorInstance.interceptors.request.use(async req => {

    const user = jwt_decode(authTokens.access)
    const isExpired = dayjs.unix(user.exp).diff(dayjs()) < 1;

    if(!isExpired) return req

    const response = await axios.post(`${baseURL}api/token/refresh/`, {
        refresh: authTokens.refresh
      });

    localStorage.setItem('authTokens', JSON.stringify(response.data))
    
    setAuthTokens(response.data)
    setUser(jwt_decode(response.data.access))
    
    req.headers.Authorization = `Bearer ${response.data.access}`
    return req
  })
      
    return interceptorInstance
}
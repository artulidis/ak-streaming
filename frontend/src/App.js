import React, { useContext } from 'react';
import {BrowserRouter as Router, Routes, Route, useRoutes} from 'react-router-dom'
import LoginPage from './pages/AuthPage';
import MainPage from './pages/MainPage';
import LayoutPage from './pages/LayoutPage';
import ProfilePage from './pages/ProfilePage';
import VideoPage from './pages/VideoPage';
import PrivateRoute from './global/PrivateRoute';
import GlobalContext from './global/GlobalContext';
import {GlobalProvider} from './global/GlobalContext'

function App() {

  return (
    <Router>
      <GlobalProvider>
      <Routes>
        <Route path='/' element={<LayoutPage/>}>

          <Route path='/' exact element={<MainPage/>}/>
          <Route path='/login' element={<LoginPage/>} />
          <Route path='/register' element={<LoginPage/>} />

          <Route path='/profile' element={<PrivateRoute/>}>
            <Route path='' exact element={<ProfilePage/>} />
          </Route>

          <Route path='/profile/:username' element={<ProfilePage />}></Route>

          <Route path='/videos/:username/:id' element={<VideoPage />}></Route>
          <Route path='/videos/:username/:id/live' element={<VideoPage />}></Route>

        </Route>
      </Routes>
      </GlobalProvider>
    </Router>
  );
}

export default App;

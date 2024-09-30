
import Market from './components/Market'
import Trade from './components/Trade'
import Error from './components/Error'

import './App.css';
import { v4 as uuidv4 } from 'uuid';
import axios from "axios";
import { Route, NavLink, BrowserRouter, Routes } from "react-router-dom";

import { ApmRoutes } from '@elastic/apm-rum-react'

// set sessionId on OTel baggage
var sessionId = uuidv4();
axios.defaults.headers.common['baggage'] = `session_id=${sessionId}`;

function App() {
  return (
    <BrowserRouter>
      <div className="App">
        <h1>TradeMaster 2000</h1>
        <NavLink to="/">Trade</NavLink> | <NavLink to="/market">Manipulate Market</NavLink> | <NavLink to="/error">Generate Errors</NavLink>
        <hr/>
        <div className="content">
          <ApmRoutes>
            <Route exact path="/" element={<Trade/>} />
            <Route path="/market" element={<Market/>} />
            <Route path="/error" element={<Error/>} />
          </ApmRoutes>
        </div>
      </div>
    </BrowserRouter>
  );
}

export default App;
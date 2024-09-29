
import Market from './components/Market'
import Trade from './components/Trade'
import './App.css';
import { v4 as uuidv4 } from 'uuid';
import axios from "axios";
import { Route, NavLink, BrowserRouter, Routes } from "react-router-dom";

// set sessionId on OTel baggage
var sessionId = uuidv4();
axios.defaults.headers.common['baggage'] = `session_id=${sessionId}`;

function App() {
  return (
    <BrowserRouter>
      <div className="App">
        <h1>TradeMaster 2000</h1>
        <NavLink to="/">Test Model</NavLink> | <NavLink to="/market">Manipulate Market</NavLink>
        <hr/>
        <div className="content">
          <Routes>
            <Route exact path="/" element={<Trade/>} />
            <Route path="/market" element={<Market/>} />
          </Routes>
        </div>
      </div>
    </BrowserRouter>
  );
}

export default App;
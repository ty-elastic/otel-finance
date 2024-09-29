import AlbumList from './components/AlbumList'
import Tester from './components/Tester'
import './App.css';
import { v4 as uuidv4 } from 'uuid';
import axios from "axios";
 
// set sessionId on OTel baggage
var sessionId = uuidv4();
axios.defaults.headers.common['baggage'] = `sessionId=${sessionId}`;

function App() {
  return (
    <div className="App">
      <AlbumList/>
      <Tester/>
    </div>
  );
}

export default App;
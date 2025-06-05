import { BrowserRouter as Router, Route, Routes } from 'react-router-dom';
import '@fortawesome/fontawesome-free/css/all.min.css';
import Home from './Home';
import { AirCondition } from './AirCondition';
import { Alarm } from './Alarm';
import './main_page.css';

function App() {
  return (
    <Router basename={process.env.REACT_APP_PUBLIC_URL || '/'}>
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/aircondition" element={<AirCondition pageTitle="Air Condition Page" />} />
        <Route path="/alarm" element={<Alarm pageTitle="Alarm Page" />} />
      </Routes>
    </Router>
  );
}

export default App;

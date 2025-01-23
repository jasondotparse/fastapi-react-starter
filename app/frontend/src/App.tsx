import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Header from './components/Header';
import 'bootstrap/dist/css/bootstrap.min.css';
import 'bootstrap/dist/js/bootstrap.bundle.min.js';
import MainPage from './pages/MainPage';
import TaskList from './pages/UserList';

const App: React.FC = () => {
  return (
    <Router>
      <Header /> {/* Display the navigation bar at the top */}
      <div className="container mt-4">
        <Routes>
          <Route path="/" element={<MainPage />} />
          <Route path="/users" element={<TaskList />} />
        </Routes>
      </div>
    </Router>
  );
};

export default App;

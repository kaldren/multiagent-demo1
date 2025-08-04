import React, { useEffect, useState } from 'react';
import './App.css';
import axios from 'axios';

function App() {
  const [fullname, setFullname] = useState('');
  const [email, setEmail] = useState('');
  const [department, setDepartment] = useState('');
  const [statusMessage, setStatusMessage] = useState('');

  const onClickOnboard = () => {
    // Here you can handle the onboarding logic
    if (!fullname || !email) {
      setStatusMessage('Please fill in both fields.');
      return;
    }
    console.log('Onboarding employee with details:', fullname, email);
    setStatusMessage('Onboarding in progress...');

    axios
      .post('http://localhost:8000/api/onboard', {
        fullname: fullname,
        email: email,
        department: department,
      })
      .then((response) => {
        if (response.data.response.startsWith('AI')) {
          setStatusMessage('🤖 ' + response.data.response);
        }
      })
      .catch((error) => {
        console.error('Error onboarding employee:', error);
        setStatusMessage('Onboarding failed.');
      });
  };

  return (
    <div className='App'>
      <h1>Onboard Employee</h1>
      <p>Please fill in the details below to onboard a new employee.</p>
      <div className='chatbox'>
        <div className='input-area'>
          <input
            type='text'
            value={fullname}
            onChange={(e) => setFullname(e.target.value)}
            placeholder='Full name'
          />
        </div>

        <div className='input-area'>
          <input
            type='email'
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            placeholder='Email address'
          />
        </div>

        <div className='input-area'>
          <input
            type='text'
            value={department}
            onChange={(e) => setDepartment(e.target.value)}
            placeholder='Department'
          />
        </div>
        <button
          style={{
            padding: '10px 20px',
            margin: '10px 0',
            backgroundColor: '#4CAF50',
            color: 'white',
            border: 'none',
            borderRadius: '5px',
            cursor: 'pointer',
          }}
          onClick={onClickOnboard}
        >
          Onboard
        </button>
      </div>
      <div className='status-bar'>
        <span className='status-message'>{statusMessage}</span>
      </div>
    </div>
  );
}

export default App;

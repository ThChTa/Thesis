import React, { useState, useEffect } from 'react';
import './main_page.css';

function Home() {
  const [jsonData, setJsonData] = useState(null);
  const [error, setError] = useState(null);

  const fetchData = async () => {
    try {
      const response = await fetch('http://192.168.1.7:5000/text'); // Direct URL
      if (!response.ok) {
        throw new Error(`HTTP error! Status: ${response.status}`);
      }
      const data = await response.json();
      setJsonData(data);
    } catch (err) {
      setError(err.message);
    }
  };

  useEffect(() => {
    fetchData();

    // Establish SSE connection
    const eventSource = new EventSource('http://192.168.1.7:5000/stream'); // Direct URL

    eventSource.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        setJsonData(data);
        setError(null); // Clear error if data is successfully received
      } catch (err) {
        setError('Failed to parse server response');
      }
    };

    eventSource.onerror = () => {
      setError('Error connecting to server');
      eventSource.close();
    };

    return () => {
      eventSource.close();
    };
  }, []);

  const getNLPText = () => {
    if (jsonData && jsonData.data && jsonData.data.length > 0) {
      return jsonData.data[jsonData.data.length - 1].nlp_text;
    }
    return '';
  };

  const getTextColor = () => {
    if (jsonData && jsonData.data && jsonData.data.length > 0) {
      const flag = jsonData.data[jsonData.data.length - 1].flag;
      if (flag === 'correct') {
        return 'green';
      } else if (flag === 'incorrect') {
        return 'red';
      }
    }
    return '';
  };

  const renderTable = () => {
    if (jsonData && jsonData.data && jsonData.data.length > 0) {
      // Reverse the data array to show the most recent data first
      const reversedData = jsonData.data.slice().reverse();
      
      return (
        <div className="table-container">
          <table>
            <thead>
              <tr className="row_0">
                <th>Command</th>
                <th>Correct/Incorrect</th>
                <th>Device</th>
                <th>Time</th>
              </tr>
            </thead>
            <tbody>
              {reversedData.map((item, index) => (
                <tr key={index}>
                  <td>{item.nlp_text}</td>
                  <td>{item.flag}</td>
                  <td>{item.device}</td>
                  <td>{item.time}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      );
    } else {
      return <p>No data available.</p>;
    }
  };

  return (
    <div>
      <div className="header">
        <h2>Starting Page</h2>
        <hr className="line-under-header" />
      </div>
      {error ? (
        <p className="text-center" style={{ color: 'red' }}>Error: {error}</p>
      ) : (
        <>
          {jsonData ? (
            <>
              <p className="text-center">
                <span style={{ color: 'black' }}><h4>Last command that got triggered:</h4></span>
                <span style={{ color: getTextColor() }}>{getNLPText()}</span>
              </p>
              <div style={{ marginTop: '50px' }}>
                {renderTable()}
              </div>
            </>
          ) : (
            <p className="text-center">Loading...</p>
          )}
        </>
      )}
    </div>
  );
}

export default Home;

import React, { useState, useEffect } from 'react';
import './alarm.css';
import BatteryIcon from './battery.png';
import ClockIcon from './clock.png';

export function Alarm({ pageTitle }) {
  const [fullData, setFullData] = useState(null); // For cards
  const [filteredData, setFilteredData] = useState(null); // For table (SSE)
  const [error, setError] = useState(null);

  const apiBaseUrl = 'http://192.168.1.7:5000';

  // Polling για κάρτες (alarm info)
  useEffect(() => {
    const fetchData = async () => {
      try {
        const response = await fetch(`${apiBaseUrl}/alarm`);
        if (!response.ok) {
          throw new Error(`HTTP error! Status: ${response.status}`);
        }
        const data = await response.json();
        setFullData(data);
      } catch (error) {
        setError('Error fetching alarm data: ' + error.message);
      }
    };

    fetchData();
    const intervalId = setInterval(fetchData, 5000);

    return () => clearInterval(intervalId);
  }, [apiBaseUrl]);

  // SSE για το table (text data)
  useEffect(() => {
    const eventSource = new EventSource(`${apiBaseUrl}/stream`);

    eventSource.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        const filtered = data.data.filter(item => item.device === 'alarm');
        setFilteredData(filtered);
        setError(null);
      } catch (err) {
        setError('Failed to parse SSE data');
      }
    };

    eventSource.onerror = () => {
      setError('Error connecting to SSE stream');
      eventSource.close();
    };

    return () => {
      eventSource.close();
    };
  }, [apiBaseUrl]);

  const normalizeOnOffValue = (value) => {
    const normalized = value ? value.toLowerCase() : '';
    return normalized === 'on' || normalized === 'off' ? normalized.charAt(0).toUpperCase() + normalized.slice(1) : 'N/A';
  };

  const formatTime = (time) => {
    if (time === 0 || time === '0') return '-';
    return time ? `${time}'` : 'N/A';
  };

  const renderAlarmCard = (property, value) => {
    const normalizedOnOff = property === 'On/Off' ? normalizeOnOffValue(value) : '';
    const isOn = normalizedOnOff === 'On';
    const isActivated = property === 'Motion Detection' && value === 'activated';

    return (
      <div className="alarm-card">
        <div className="alarm-card-content">
          {(property === 'On/Off' || property === 'Motion Detection') && (
            <div className={`alarm-status-circle ${property === 'On/Off' ? (isOn ? 'on' : 'off') : (isActivated ? 'on' : 'off')}`}></div>
          )}
          {(property === 'Battery' && <img src={BatteryIcon} alt="Battery Icon" className="battery-icon" />) ||
            (property === 'Timer' && <img src={ClockIcon} alt="Clock Icon" className="clock-icon" />)}
          <div className="alarm-info">
            <div className="alarm-property">{property}</div>
            <div className="alarm-value">
              {property === 'Battery' ? value + '%' : property === 'Timer' ? formatTime(value) : value}
            </div>
          </div>
        </div>
      </div>
    );
  };

  if (error) {
    return <p className="text-center" style={{ color: 'red' }}>{error}</p>;
  }

  return (
    <div className="alarm-page-container">
      <div className="header">
        <h1>{pageTitle}</h1>
        <hr className="line-under-header" />
      </div>

      {fullData ? (
        <div className="alarm-cards-container">
          {renderAlarmCard('On/Off', fullData.on_off || 'N/A')}
          {renderAlarmCard('Battery', fullData.battery || 'N/A')}
          {renderAlarmCard('Timer', fullData.timer || '0')}
          {renderAlarmCard('Motion Detection', fullData.motion_detection || 'N/A')}
        </div>
      ) : (
        <p>Loading data...</p>
      )}

      {filteredData && (
        <div className="tables-container">
          <div className="table-container-wrapper">
            <h2>Alarm Information</h2>
            <div className="table-container">
              <table className="table-container2">
                <thead>
                  <tr className="row_0">
                    <th>Original Text</th>
                    <th>NLP Text</th>
                    <th>Device</th>
                    <th>Flag</th>
                    <th>Time</th>
                  </tr>
                </thead>
                <tbody>
                  {filteredData
                    .filter(item => item.flag === 'correct')
                    .slice()
                    .reverse()
                    .map((item, index) => (
                      <tr key={index}>
                        <td>{item.original_text}</td>
                        <td>{item.nlp_text}</td>
                        <td>{item.device}</td>
                        <td>{item.flag}</td>
                        <td>{item.time}</td>
                      </tr>
                    ))}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default Alarm;

import React, { useState, useEffect } from 'react';
import './air_condition.css';
import HeatIcon from './hot.png';
import SnowflakeIcon from './snowflake.png';
import AutoIcon from './letter-a.png';
import ClockIcon from './clock.png';
import ThermometerIcon from './thermometer.png';

export function AirCondition({ pageTitle }) {
  const [mainData, setMainData] = useState(null); // Για τις κάρτες
  const [filteredData, setFilteredData] = useState(null); // Για το table
  const [error, setError] = useState(null);

  const apiBaseUrl = 'http://192.168.96.150:5000';

  // Polling για τις κάρτες
  useEffect(() => {
    const fetchData = async () => {
      try {
        const response = await fetch(`${apiBaseUrl}/air_condition`);
        if (!response.ok) {
          throw new Error(`HTTP error! Status: ${response.status}`);
        }
        const data = await response.json();
        setMainData(data);
      } catch (error) {
        setError('Error fetching air condition data: ' + error.message);
      }
    };

    fetchData();
    const intervalId = setInterval(fetchData, 5000);

    return () => clearInterval(intervalId);
  }, [apiBaseUrl]);

  // SSE για το table
  useEffect(() => {
    const eventSource = new EventSource(`${apiBaseUrl}/stream`);

    eventSource.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        const filtered = data.data.filter(item => item.device === 'air condition');
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

  const formatTime = (time) => {
    if (time === 0 || time === '0') return '-';
    return time ? `${time}'` : 'N/A';
  };

  const renderAirConditionCard = (property, value) => {
    let statusClass = '';
    let icon = null;

    if (property === 'On/Off') {
      statusClass = value?.toLowerCase() === 'on' ? 'on' : 'off';
    }

    if (property === 'Mode') {
      if (value === 'heat') icon = HeatIcon;
      else if (value === 'cold') icon = SnowflakeIcon;
      else if (value === 'auto') icon = AutoIcon;
    } else if (property === 'Timer') {
      icon = ClockIcon;
    } else if (property === 'Temperature') {
      icon = ThermometerIcon;
    }

    return (
      <div className={`air-condition-card ${statusClass}`}>
        <div className="air-condition-card-content">
          {statusClass && <div className={`air-condition-status-circle ${statusClass}`}></div>}
          {icon && <img src={icon} alt={`${property} Icon`} className="air-condition-icon" />}
          <div className="air-condition-info">
            <div className="air-condition-property">{property}</div>
            <div className="air-condition-value">
              {property === 'Temperature' ? `${value}°C` : property === 'Timer' ? formatTime(value) : value}
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
    <div className="air-condition-page-container">
      <div className="header">
        <h1>{pageTitle}</h1>
        <hr className="line-under-header" />
      </div>

      {mainData ? (
        <div className="air-condition-cards-container">
          {renderAirConditionCard('On/Off', mainData.on_off || 'N/A')}
          {renderAirConditionCard('Temperature', mainData.temperature || 'N/A')}
          {renderAirConditionCard('Timer', mainData.timer || '0')}
          {renderAirConditionCard('Mode', mainData.mode || 'N/A')}
        </div>
      ) : (
        <p>Loading data...</p>
      )}

      {filteredData && (
        <div className="tables-container">
          <div className="table-container-wrapper">
            <h2>Air Condition Information</h2>
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

export default AirCondition;

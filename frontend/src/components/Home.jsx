import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { MapContainer, TileLayer, Marker, Popup } from 'react-leaflet';
import 'leaflet/dist/leaflet.css';
import L from 'leaflet';
import { floodAPI } from '../services/api';

// Fix for default markers
delete L.Icon.Default.prototype._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl: require('leaflet/dist/images/marker-icon-2x.png'),
  iconUrl: require('leaflet/dist/images/marker-icon.png'),
  shadowUrl: require('leaflet/dist/images/marker-shadow.png'),
});

function Home() {
  const [stats, setStats] = useState(null);
  const [reports, setReports] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      const [statsResponse, reportsResponse] = await Promise.all([
        floodAPI.getStats(),
        floodAPI.getFloods()
      ]);
      setStats(statsResponse.data);
      setReports(reportsResponse.data);
      setLoading(false);
    } catch (err) {
      setError('Failed to load data');
      setLoading(false);
    }
  };

  if (loading) return <div className="loading">Loading...</div>;
  if (error) return <div className="error">{error}</div>;

  const severityColors = {
    Low: '#28a745',
    Medium: '#ffc107',
    High: '#fd7e14',
    Critical: '#dc3545'
  };

  const createCustomIcon = (severity) => {
    const color = severityColors[severity] || '#0066cc';
    return L.divIcon({
      className: 'custom-marker',
      html: `<div style="background-color: ${color}; width: 24px; height: 24px; border-radius: 50%; border: 3px solid white; box-shadow: 0 2px 8px rgba(0,0,0,0.3);"></div>`,
      iconSize: [24, 24],
      iconAnchor: [12, 12],
    });
  };

  return (
    <div className="home">
      <div className="hero-section">
        <h1>UK Flood Reporting System</h1>
        <p className="subtitle">Report local flood incidents and view floods on an interactive map</p>

        <div className="action-buttons">
          <Link to="/report" className="btn btn-primary">Report a Flood</Link>
          <Link to="/map" className="btn btn-secondary">View Full Map</Link>
        </div>
      </div>

      <div className="home-grid">
        <div className="stats-section">
          <h2>Live Statistics</h2>
          {stats && (
            <div className="stats-grid">
              <div className="stat-card total">
                <div className="stat-value">{stats.total_active}</div>
                <div className="stat-label">Active Reports</div>
              </div>
              {stats.by_severity && Object.entries(stats.by_severity).map(([severity, count]) => (
                <div key={severity} className={`stat-card severity-${severity.toLowerCase()}`}>
                  <div className="stat-value">{count}</div>
                  <div className="stat-label">{severity}</div>
                </div>
              ))}
            </div>
          )}
        </div>

        <div className="map-preview">
          <h2>Recent Floods</h2>
          <div className="map-container-home">
            <MapContainer
              center={[54.0, -2.5]}
              zoom={6}
              minZoom={3}
              maxZoom={18}
              maxBounds={[[-90, -180], [90, 180]]}
              maxBoundsViscosity={1.0}
              style={{ height: '100%', width: '100%', borderRadius: '20px' }}
            >
              <TileLayer
                url="https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png"
                attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
                noWrap={true}
              />
              {reports.map((report) => (
                <Marker
                  key={report.id}
                  position={[report.latitude, report.longitude]}
                  icon={createCustomIcon(report.severity)}
                >
                  <Popup>
                    <div className="popup-content">
                      <h4>{report.severity} Severity</h4>
                      {report.address && <p><strong>Location:</strong> {report.address}</p>}
                      {report.description && <p>{report.description}</p>}
                      <p><small>{new Date(report.created_at).toLocaleDateString()}</small></p>
                    </div>
                  </Popup>
                </Marker>
              ))}
            </MapContainer>
          </div>
        </div>
      </div>
    </div>
  );
}

export default Home;

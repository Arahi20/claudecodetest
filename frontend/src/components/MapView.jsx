import React, { useState, useEffect } from 'react';
import { MapContainer, TileLayer, Marker, Popup } from 'react-leaflet';
import { floodAPI } from '../services/api';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';

// Fix for default marker icons in React Leaflet
delete L.Icon.Default.prototype._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl: require('leaflet/dist/images/marker-icon-2x.png'),
  iconUrl: require('leaflet/dist/images/marker-icon.png'),
  shadowUrl: require('leaflet/dist/images/marker-shadow.png'),
});

// Custom marker colors based on severity
const getMarkerIcon = (severity) => {
  const colors = {
    Low: '#28a745',
    Medium: '#ffc107',
    High: '#fd7e14',
    Critical: '#dc3545',
  };

  return L.divIcon({
    className: 'custom-marker',
    html: `<div style="background-color: ${colors[severity]}; width: 25px; height: 25px; border-radius: 50%; border: 2px solid white;"></div>`,
    iconSize: [25, 25],
    iconAnchor: [12, 12],
  });
};

function MapView() {
  const [floods, setFloods] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [filters, setFilters] = useState({
    severity: '',
    startDate: '',
    endDate: '',
    status: 'Active',
  });

  useEffect(() => {
    fetchFloods();
  }, [filters]);

  const fetchFloods = async () => {
    try {
      setLoading(true);
      const response = await floodAPI.getFloods(filters);
      setFloods(response.data);
      setLoading(false);
    } catch (err) {
      setError('Failed to load flood reports');
      setLoading(false);
    }
  };

  const handleFilterChange = (e) => {
    setFilters({
      ...filters,
      [e.target.name]: e.target.value,
    });
  };

  const resetFilters = () => {
    setFilters({
      severity: '',
      startDate: '',
      endDate: '',
      status: 'Active',
    });
  };

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleString();
  };

  return (
    <div className="map-view">
      <h1>Flood Reports Map</h1>

      <div className="map-layout">
        <div className="filter-sidebar">
          <h3>Filters</h3>

          <div className="filter-group">
            <label>Severity</label>
            <select name="severity" value={filters.severity} onChange={handleFilterChange}>
              <option value="">All</option>
              <option value="Low">Low</option>
              <option value="Medium">Medium</option>
              <option value="High">High</option>
              <option value="Critical">Critical</option>
            </select>
          </div>

          <div className="filter-group">
            <label>Status</label>
            <select name="status" value={filters.status} onChange={handleFilterChange}>
              <option value="">All</option>
              <option value="Active">Active</option>
              <option value="Resolved">Resolved</option>
            </select>
          </div>

          <div className="filter-group">
            <label>Start Date</label>
            <input
              type="date"
              name="startDate"
              value={filters.startDate}
              onChange={handleFilterChange}
            />
          </div>

          <div className="filter-group">
            <label>End Date</label>
            <input
              type="date"
              name="endDate"
              value={filters.endDate}
              onChange={handleFilterChange}
            />
          </div>

          <button onClick={resetFilters} className="btn btn-secondary">
            Reset Filters
          </button>

          <div className="legend">
            <h4>Legend</h4>
            <div className="legend-item">
              <span className="legend-color" style={{ backgroundColor: '#28a745' }}></span>
              Low
            </div>
            <div className="legend-item">
              <span className="legend-color" style={{ backgroundColor: '#ffc107' }}></span>
              Medium
            </div>
            <div className="legend-item">
              <span className="legend-color" style={{ backgroundColor: '#fd7e14' }}></span>
              High
            </div>
            <div className="legend-item">
              <span className="legend-color" style={{ backgroundColor: '#dc3545' }}></span>
              Critical
            </div>
          </div>

          <div className="report-count">
            <strong>{floods.length}</strong> reports found
          </div>
        </div>

        <div className="map-main">
          {loading && <div className="loading">Loading flood reports...</div>}
          {error && <div className="error">{error}</div>}

          {!loading && !error && (
            <MapContainer
              center={[54.5, -2.5]}
              zoom={6}
              minZoom={3}
              maxZoom={18}
              maxBounds={[[-90, -180], [90, 180]]}
              maxBoundsViscosity={1.0}
              style={{ height: '100%', width: '100%' }}
            >
              <TileLayer
                url="https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png"
                attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
                noWrap={true}
              />

              {floods.map((flood) => (
                <Marker
                  key={flood.id}
                  position={[flood.latitude, flood.longitude]}
                  icon={getMarkerIcon(flood.severity)}
                >
                  <Popup>
                    <div className="popup-content">
                      <h4>Severity: {flood.severity}</h4>
                      {flood.address && <p><strong>Address:</strong> {flood.address}</p>}
                      {flood.description && <p><strong>Description:</strong> {flood.description}</p>}
                      <p><strong>Reported:</strong> {formatDate(flood.created_at)}</p>
                      <p><strong>Status:</strong> {flood.status}</p>
                      {flood.photo_url && (
                        <img
                          src={`http://localhost:5001${flood.photo_url}`}
                          alt="Flood"
                          style={{ maxWidth: '200px', marginTop: '10px' }}
                        />
                      )}
                    </div>
                  </Popup>
                </Marker>
              ))}
            </MapContainer>
          )}
        </div>
      </div>
    </div>
  );
}

export default MapView;

import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { floodAPI } from '../services/api';
import { MapContainer, TileLayer, Marker, useMapEvents } from 'react-leaflet';
import 'leaflet/dist/leaflet.css';

function LocationPicker({ position, setPosition }) {
  useMapEvents({
    click(e) {
      setPosition([e.latlng.lat, e.latlng.lng]);
    },
  });

  return position ? <Marker position={position} /> : null;
}

function ReportForm() {
  const navigate = useNavigate();
  const [formData, setFormData] = useState({
    latitude: '',
    longitude: '',
    address: '',
    severity: 'Medium',
    description: '',
  });
  const [position, setPosition] = useState([54.5, -2.5]); // UK center
  const [photo, setPhoto] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(false);

  const handlePositionChange = (newPosition) => {
    setPosition(newPosition);
    setFormData({
      ...formData,
      latitude: newPosition[0],
      longitude: newPosition[1],
    });
  };

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value,
    });
  };

  const handleFileChange = (e) => {
    setPhoto(e.target.files[0]);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    try {
      let photoUrl = null;

      // Upload photo if provided
      if (photo) {
        const uploadResponse = await floodAPI.uploadPhoto(photo);
        photoUrl = uploadResponse.data.url;
      }

      // Create flood report
      const reportData = {
        ...formData,
        latitude: parseFloat(formData.latitude),
        longitude: parseFloat(formData.longitude),
        photo_url: photoUrl,
      };

      await floodAPI.createFlood(reportData);
      setSuccess(true);
      setTimeout(() => navigate('/map'), 2000);
    } catch (err) {
      setError(err.response?.data?.error || 'Failed to submit report');
      setLoading(false);
    }
  };

  if (success) {
    return (
      <div className="success-message">
        <h2>Report Submitted Successfully!</h2>
        <p>Redirecting to map...</p>
      </div>
    );
  }

  return (
    <div className="report-form">
      <h1>Report a Flood</h1>

      <form onSubmit={handleSubmit}>
        <div className="form-section">
          <h3>Location</h3>
          <p>Click on the map to select the flood location</p>

          <div className="map-container">
            <MapContainer
              center={position}
              zoom={6}
              style={{ height: '400px', width: '100%' }}
            >
              <TileLayer
                url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
                attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
              />
              <LocationPicker position={position} setPosition={handlePositionChange} />
            </MapContainer>
          </div>

          <div className="form-row">
            <div className="form-group">
              <label>Latitude</label>
              <input
                type="number"
                step="any"
                name="latitude"
                value={formData.latitude}
                onChange={handleChange}
                required
              />
            </div>
            <div className="form-group">
              <label>Longitude</label>
              <input
                type="number"
                step="any"
                name="longitude"
                value={formData.longitude}
                onChange={handleChange}
                required
              />
            </div>
          </div>

          <div className="form-group">
            <label>Address (Optional)</label>
            <input
              type="text"
              name="address"
              value={formData.address}
              onChange={handleChange}
              placeholder="e.g., 123 Main St, London"
            />
          </div>
        </div>

        <div className="form-section">
          <h3>Flood Details</h3>

          <div className="form-group">
            <label>Severity Level *</label>
            <select
              name="severity"
              value={formData.severity}
              onChange={handleChange}
              required
            >
              <option value="Low">Low</option>
              <option value="Medium">Medium</option>
              <option value="High">High</option>
              <option value="Critical">Critical</option>
            </select>
          </div>

          <div className="form-group">
            <label>Description</label>
            <textarea
              name="description"
              value={formData.description}
              onChange={handleChange}
              rows="4"
              placeholder="Describe the flooding situation..."
            />
          </div>

          <div className="form-group">
            <label>Photo (Optional)</label>
            <input
              type="file"
              accept="image/*"
              onChange={handleFileChange}
            />
          </div>
        </div>

        {error && <div className="error-message">{error}</div>}

        <div className="form-actions">
          <button
            type="button"
            onClick={() => navigate('/')}
            className="btn btn-secondary"
          >
            Cancel
          </button>
          <button
            type="submit"
            disabled={loading}
            className="btn btn-primary"
          >
            {loading ? 'Submitting...' : 'Submit Report'}
          </button>
        </div>
      </form>
    </div>
  );
}

export default ReportForm;

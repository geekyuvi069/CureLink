import React, { useState } from 'react';

const Signup = ({ onSignup, onSwitchToLogin }) => {
  const [formData, setFormData] = useState({
    email: '',
    password: '',
    full_name: '',
    role: 'patient',
  });
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    setIsLoading(true);
    setError('');

    try {
      const response = await fetch('http://localhost:8000/api/auth/register', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(formData),
      });

      const data = await response.json();

      if (response.ok) {
        onSignup(data);
      } else {
        setError(data.detail || 'Registration failed.');
      }
    } catch (err) {
      setError('Connection error.');
    } finally {
      setIsLoading(false);
    }
  };

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  return (
    <div className="auth-card">
      <h2 style={{ marginBottom: '1.5rem', textAlign: 'center' }}>Sign Up</h2>
      <form onSubmit={handleSubmit}>
        <div style={{ display: 'flex', gap: '0.5rem', marginBottom: '1rem' }}>
          <button
            type="button"
            style={{
              flex: 1,
              padding: '0.5rem',
              borderRadius: '4px',
              border: '1px solid #ddd',
              background: formData.role === 'patient' ? '#2563eb' : 'white',
              color: formData.role === 'patient' ? 'white' : 'black',
              cursor: 'pointer'
            }}
            onClick={() => setFormData({ ...formData, role: 'patient' })}
          >
            Patient
          </button>
          <button
            type="button"
            style={{
              flex: 1,
              padding: '0.5rem',
              borderRadius: '4px',
              border: '1px solid #ddd',
              background: formData.role === 'doctor' ? '#2563eb' : 'white',
              color: formData.role === 'doctor' ? 'white' : 'black',
              cursor: 'pointer'
            }}
            onClick={() => setFormData({ ...formData, role: 'doctor' })}
          >
            Doctor
          </button>
        </div>
        <input
          className="input-field"
          type="text"
          name="full_name"
          placeholder="Full Name"
          value={formData.full_name}
          onChange={handleChange}
          required
        />
        <input
          className="input-field"
          type="email"
          name="email"
          placeholder="Email Address"
          value={formData.email}
          onChange={handleChange}
          required
        />
        <input
          className="input-field"
          type="password"
          name="password"
          placeholder="Password"
          value={formData.password}
          onChange={handleChange}
          required
        />
        {error && <div style={{ color: 'red', marginBottom: '1rem', fontSize: '0.875rem' }}>{error}</div>}
        <button type="submit" className="btn-primary" disabled={isLoading}>
          {isLoading ? 'Creating Account...' : 'Sign Up'}
        </button>
      </form>
      <div style={{ marginTop: '1rem', textAlign: 'center', fontSize: '0.875rem' }}>
        Already have an account? <span style={{ color: '#2563eb', cursor: 'pointer' }} onClick={onSwitchToLogin}>Login</span>
      </div>
    </div>
  );
};

export default Signup;

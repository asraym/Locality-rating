import React, { useState } from 'react';
import './App.css';
import SearchBar from './components/SearchBar';
import RatingCard from './components/RatingCard';
import { searchLocality } from './mockData';

function App() {
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);

  const handleSearch = async (locality) => {
    setLoading(true);
    setError(null);
    setResult(null);

    try {
      const data = await searchLocality(locality);
      setResult(data);
    } catch (err) {
      setError(`Locality "${locality}" not found. Try: Brooklyn Heights, New York`);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="App">
      <header className="app-header">
        <h1>🏘️ Locality Intelligence Platform</h1>
        <p>AI-Powered Real Estate Investment Analysis</p>
      </header>

      <main className="app-main">
        <SearchBar onSearch={handleSearch} loading={loading} />

        {loading && (
          <div className="loading">
            <div className="spinner"></div>
            <p>Analyzing locality data...</p>
          </div>
        )}

        {error && (
          <div className="error">
            <p>{error}</p>
          </div>
        )}

        {result && <RatingCard data={result} />}
      </main>

      <footer className="app-footer">
        <p>Built with React + Python FastAPI | Data from Google Maps, Reddit & News APIs</p>
      </footer>
    </div>
  );
}

export default App;
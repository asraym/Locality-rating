import React, { useState } from 'react';

function SearchBar({ onSearch, loading }) {
  const [searchInput, setSearchInput] = useState('');

  const handleSubmit = (e) => {
    e.preventDefault();
    if (searchInput.trim()) {
      onSearch(searchInput);
    }
  };

  // Popular localities for quick access
  const popularLocalities = [
    "Brooklyn Heights, New York",
    "Koramangala, Bangalore",
    "Whitefield, Bangalore"
  ];

  return (
    <div className="search-container">
      <form onSubmit={handleSubmit}>
        <input
          type="text"
          value={searchInput}
          onChange={(e) => setSearchInput(e.target.value)}
          placeholder="Search locality (e.g., Brooklyn Heights, New York)"
          className="search-input"
          disabled={loading}
        />
        <button type="submit" className="search-button" disabled={loading}>
          {loading ? 'Searching...' : 'Search'}
        </button>
      </form>

      <div className="popular-searches">
        <p>Popular searches:</p>
        {popularLocalities.map((locality) => (
          <button
            key={locality}
            onClick={() => onSearch(locality)}
            className="popular-button"
            disabled={loading}
          >
            {locality}
          </button>
        ))}
      </div>
    </div>
  );
}

export default SearchBar;
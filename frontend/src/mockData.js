export const mockLocalityData = {
  "Brooklyn Heights, New York": {
    locality: "Brooklyn Heights, New York",
    final_score: 78.5,
    confidence: 85,
    confidence_level: "High",
    recommendation: "BUY",
    reasoning: "Strong fundamentals and excellent location",
    component_scores: {
      sentiment: 75.2,
      infrastructure: 88.0,
      real_estate: 72.5,
      developers: 80.0,
      projects: 65.0,
      amenities: 82.0,
      crime: 90.0
    },
    key_insights: [
      "Excellent subway connectivity (0.5km)",
      "Multiple hospitals nearby (3)",
      "Strong rental yield (3.8%)",
      "Low crime rate",
      "High-quality schools (12 within 3km)"
    ],
    risks: [
      "Above city average pricing (15% premium)"
    ]
  },
  "Koramangala, Bangalore": {
    locality: "Koramangala, Bangalore",
    final_score: 74.0,
    confidence: 92,
    confidence_level: "High",
    recommendation: "HOLD",
    reasoning: "Good potential but premium pricing",
    component_scores: {
      sentiment: 79.2,
      infrastructure: 90.0,
      real_estate: 60.0,
      developers: 100.0,
      projects: 54.6,
      amenities: 28.0,
      crime: 50.0
    },
    key_insights: [
      "Excellent metro connectivity (1.2km)",
      "Premium developer presence",
      "High user engagement (380 mentions)",
      "Good educational infrastructure"
    ],
    risks: [
      "Above city average pricing (35% premium)",
      "Slower infrastructure development"
    ]
  },
  "Whitefield, Bangalore": {
    locality: "Whitefield, Bangalore",
    final_score: 70.2,
    confidence: 88,
    confidence_level: "High",
    recommendation: "HOLD",
    reasoning: "Decent potential but monitor trends",
    component_scores: {
      sentiment: 70.8,
      infrastructure: 80.0,
      real_estate: 65.0,
      developers: 80.0,
      projects: 78.0,
      amenities: 21.2,
      crime: 75.0
    },
    key_insights: [
      "Good metro connectivity (2.5km)",
      "Strong developer presence (4 reputed brands)",
      "Metro expansion planned (under construction)",
      "IT Park development (2 years)"
    ],
    risks: [
      "Above city average pricing (15% premium)"
    ]
  }
};

// Function to simulate API call
export const searchLocality = (localityName) => {
  return new Promise((resolve, reject) => {
    // Simulate network delay
    setTimeout(() => {
      const result = mockLocalityData[localityName];
      if (result) {
        resolve(result);
      } else {
        reject(new Error("Locality not found"));
      }
    }, 1500); // 1.5 second delay to simulate real API
  });
};
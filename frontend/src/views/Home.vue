<template>
  <div class="container mt-4">
    <div class="text-center mb-4">
      <h2>AI-Powered Travel Recommendations</h2>
      <p class="text-muted">Get personalized suggestions for your New Zealand adventure</p>
    </div>

    <div class="card mb-4">
      <div class="card-body">
        <h5 class="card-title">Plan Your Trip</h5>
        <form @submit.prevent="getRecommendations">
          <!-- Simplified Interface -->
          <div class="row" v-if="!showAdvanced">
            <div class="col-md-6 mb-3">
              <label class="form-label">Destination</label>
              <select v-model="location.address" class="form-control" @change="updateLocation">
                <option v-for="(coords, city) in locations" :key="city" :value="city">{{ city }}</option>
              </select>
            </div>

            <div class="col-md-6 mb-3">
              <label class="form-label">Trip Duration (days)</label>
              <input v-model.number="preferences.duration" type="number" min="1" max="30" class="form-control" 
                     @input="validateDuration" />
              <div v-if="durationWarning" class="text-warning small mt-1">
                {{ durationWarning }}
              </div>
            </div>
          </div>

          <!-- Advanced Options -->
          <div v-if="showAdvanced">
            <div class="row mb-3">
              <div class="col-md-6 mb-3">
                <label class="form-label">Destination</label>
                <select v-model="location.address" class="form-control" @change="updateLocation">
                  <option v-for="(coords, city) in locations" :key="city" :value="city">{{ city }}</option>
                </select>
              </div>

              <div class="col-md-6 mb-3">
                <label class="form-label">Trip Duration (days)</label>
                <input v-model.number="preferences.duration" type="number" min="1" max="30" class="form-control"
                       @input="validateDuration" />
                <div v-if="durationWarning" class="text-warning small mt-1">
                  {{ durationWarning }}
                </div>
              </div>
            </div>

            <div class="row mb-3">
              <div class="col-md-6 mb-3">
                <label class="form-label">Activity Types</label>
                <div style="max-height: 120px; overflow-y: auto; border: 1px solid #dee2e6; border-radius: 4px; padding: 8px;">
                  <div class="form-check form-check-inline" v-for="activity in activityOptions" :key="activity">
                    <input
                      class="form-check-input"
                      type="checkbox"
                      :id="activity"
                      :value="activity"
                      v-model="preferences.activity_types"
                    />
                    <label class="form-check-label" :for="activity" style="font-size: 0.9em;">
                      {{ activity }}
                    </label>
                  </div>
                </div>
              </div>

              <div class="col-md-6 mb-3">
                <label class="form-label">Budget (NZD)</label>
                <div class="input-group">
                  <input v-model.number="preferences.budget_range[0]" type="number" class="form-control" placeholder="Min" />
                  <span class="input-group-text">-</span>
                  <input v-model.number="preferences.budget_range[1]" type="number" class="form-control" placeholder="Max" />
                </div>
              </div>
            </div>

            <div class="row mb-3">
              <div class="col-md-6 mb-3">
                <label class="form-label">Travel Style</label>
                <select v-model="preferences.travel_style" class="form-control">
                  <option value="adventure">Adventure</option>
                  <option value="relaxing">Relaxing</option>
                  <option value="cultural">Cultural</option>
                  <option value="family">Family</option>
                </select>
              </div>

              <div class="col-md-6 mb-3">
                <label class="form-label">Group Size</label>
                <input v-model.number="preferences.group_size" type="number" min="1" class="form-control" />
              </div>
            </div>

            <div class="row mb-3">
              <div class="col-md-6 mb-3">
                <label class="form-label">Max Distance from Destination (km)</label>
                <div class="d-flex align-items-center">
                  <input v-model.number="preferences.max_travel_distance" 
                         type="range" min="25" max="300" step="25" 
                         class="form-range flex-grow-1 me-2" />
                  <span class="badge bg-secondary">{{ preferences.max_travel_distance }}km</span>
                </div>
              </div>
            </div>
          </div>

          <div class="text-center">
            <button type="submit" class="btn btn-primary me-2" :disabled="loading">
              {{ loading ? 'Planning...' : 'Plan My Trip' }}
            </button>
            <button type="button" class="btn btn-outline-secondary btn-sm" @click="toggleAdvanced">
              {{ showAdvanced ? 'Less Options' : 'More Options' }}
            </button>
            <button v-if="isLoggedIn" @click="savePreferences" type="button" class="btn btn-outline-secondary btn-sm ms-2">
              Save Preferences
            </button>
          </div>
        </form>
      </div>
    </div>

    <div v-if="loading" class="text-center py-4">
      <div class="spinner-border" role="status"></div>
      <p class="mt-2">Creating your personalized itinerary...</p>
    </div>

    <div v-if="error" class="alert alert-danger">
      {{ error }}
      <button type="button" class="btn-close float-end" @click="error = null"></button>
    </div>

    <!-- Itinerary Planning Results -->
    <div v-if="itinerary.length && !loading" class="mb-4">
      <h4 class="mb-3">Your {{ preferences.duration }}-Day Itinerary</h4>
      
      <div class="row">
        <div class="col-lg-8">
          <!-- Daily Itinerary -->
          <div class="accordion" id="itineraryAccordion">
            <div class="accordion-item" v-for="(day, index) in itinerary" :key="index">
              <h2 class="accordion-header">
                <button class="accordion-button" :class="{ collapsed: index !== 0 }" type="button" 
                        :data-bs-toggle="'collapse'" :data-bs-target="`#day${index + 1}`">
                  <strong>Day {{ index + 1 }}</strong>
                  <span class="ms-2 text-muted">{{ day.attractions.length }} attractions</span>
                </button>
              </h2>
              <div :id="`day${index + 1}`" class="accordion-collapse collapse" :class="{ show: index === 0 }"
                   data-bs-parent="#itineraryAccordion">
                <div class="accordion-body">
                  <div class="row">
                    <div class="col-md-6 mb-3" v-for="attraction in day.attractions" :key="attraction.id">
                      <div class="card h-100">
                        <div class="card-body">
                          <h6 class="card-title">{{ attraction.name }}</h6>
                          <p class="card-text small">{{ attraction.description }}</p>
                          
                          <div class="d-flex justify-content-between align-items-center mb-2">
                            <span class="badge bg-primary">{{ attraction.category }}</span>
                            <span class="badge bg-warning text-dark">★ {{ attraction.rating }}</span>
                          </div>

                          <div class="small text-muted mb-2">
                            <div>Price: ${{ attraction.price_range[0] }} - ${{ attraction.price_range[1] }}</div>
                            <div v-if="attraction.distance">Distance: {{ attraction.distance }}km</div>
                            <div>Time: {{ attraction.estimated_time }}</div>
                          </div>

                          <div v-if="attraction.reasons && attraction.reasons.length" class="small">
                            <strong>Why:</strong>
                            <ul class="mb-1" style="padding-left: 1rem;">
                              <li v-for="reason in attraction.reasons.slice(0,2)" :key="reason">{{ reason }}</li>
                            </ul>
                          </div>
                        </div>
                        

                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
        
        <div class="col-lg-4">
          <div class="card sticky-top">
            <div class="card-header">
              <h6 class="mb-0">Trip Overview</h6>
            </div>
            <div class="card-body">
              <div class="mb-3">
                <strong>Destination:</strong> {{ location.address }}<br>
                <strong>Duration:</strong> {{ preferences.duration }} days<br>
                <strong>Total Attractions:</strong> {{ totalAttractions }}<br>
                <strong>Budget Range:</strong> ${{ minBudget }} - ${{ maxBudget }}
              </div>

              <!-- Weather Information -->
              <div class="card mb-3" v-if="weatherInfo">
                <div class="card-header">
                  <h6 class="mb-0">Current Weather</h6>
                </div>
                <div class="card-body p-2">
                  <div class="d-flex align-items-center">
                    <div class="weather-icon me-2">
                      {{ weatherInfo.condition === 'sunny' ? '☀️' : 
                         weatherInfo.condition === 'cloudy' ? '☁️' : 
                         weatherInfo.condition === 'rainy' ? '🌧️' : '🌤️' }}
                    </div>
                    <div>
                      <div><strong>{{ weatherInfo.temperature }}°C</strong></div>
                      <div class="small text-muted">{{ weatherInfo.condition }}</div>
                      <div class="small" :class="weatherInfo.suitable_for_outdoor ? 'text-success' : 'text-warning'">
                        {{ weatherInfo.suitable_for_outdoor ? '✓ Good for outdoor activities' : '⚠️ Consider indoor activities' }}
                      </div>
                    </div>
                  </div>
                </div>
              </div>
              
              <div class="card">
                <div class="card-header">
                  <h6 class="mb-0">Locations Map</h6>
                </div>
                <div class="card-body p-0">
                  <div ref="mapContainer" style="height: 300px; width: 100%; position: relative;"></div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- All Recommendations (fallback) -->
    <div v-if="recommendations.length && !itinerary.length && !loading">
      <h4 class="mb-3">Recommended Attractions</h4>
      
      <div class="row">
        <div class="col-md-4 mb-3" v-for="rec in recommendations" :key="rec.id">
          <div class="card h-100">
            <div class="card-body">
              <h6 class="card-title">{{ rec.name }}</h6>
              <p class="card-text small">{{ rec.description }}</p>
              
              <div class="d-flex justify-content-between align-items-center mb-2">
                <span class="badge bg-primary">{{ rec.category }}</span>
                <span class="badge bg-warning text-dark">★ {{ rec.rating }}</span>
              </div>

              <div class="small text-muted mb-2">
                Price: ${{ rec.price_range[0] }} - ${{ rec.price_range[1] }}
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>



    <div v-if="!recommendations.length && !loading && !error">
      <h4>Popular Destinations</h4>
      <p class="text-muted">Choose your destination and duration above to get started</p>
      
      <div class="row">
        <div class="col-md-4 mb-3" v-for="attraction in defaultAttractions" :key="attraction.id">
          <div class="card">
            <img :src="attraction.image" class="card-img-top" style="height: 150px; object-fit: cover;" :alt="attraction.name">
            <div class="card-body p-3">
              <h6 class="card-title">{{ attraction.name }}</h6>
              <p class="card-text small">{{ attraction.description }}</p>
              <div>
                <span class="badge bg-primary me-1">{{ attraction.category }}</span>
                <span class="badge bg-warning text-dark">★ {{ attraction.rating }}</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import L from 'leaflet'


const API_BASE_URL = 'http://travelplannerbackend-env.eba-p7nfszip.us-east-1.elasticbeanstalk.com';
export default {
  name: 'Home',
  data() {
    return {
      loading: false,
      error: null,
      recommendations: [],
      itinerary: [],
      map: null,
      mapInitialized: false,
      showAdvanced: false,
      durationWarning: '',
      weatherInfo: null,
      activityOptions: ['natural', 'scenic', 'adventure', 'cultural', 'family', 'historical'],
      preferences: {
        activity_types: ['natural', 'scenic'],
        budget_range: [100, 400],
        travel_style: 'adventure',
        difficulty_preference: 'medium',
        max_travel_distance: 50, // Default 50km
        group_size: 2,
        duration: 3,
        season: 'summer',
        is_outdoor: true
      },
      location: {
        address: 'Wellington, New Zealand',
        lat: -41.3,
        lng: 174.8
      },
      locations: {
        'Wellington, New Zealand': { lat: -41.3, lng: 174.8 },
        'Hamilton, New Zealand': { lat: -37.7870, lng: 175.2793 },
        'Auckland, New Zealand': { lat: -36.8485, lng: 174.7633 },
        'Christchurch, New Zealand': { lat: -43.5320, lng: 172.6306 }
      },
              savedItineraries: [],
      defaultAttractions: [
        {
          id: 1,
          name: "Milford Sound",
          description: "Famous fiord in Fiordland National Park",
          category: "nature",
          rating: 4.8,
          image: "/images/milford-sound.webp"
        },
        {
          id: 2,
          name: "Queenstown Skyline Gondola",
          description: "Scenic gondola ride",
          category: "adventure",
          rating: 4.6,
          image: "/images/skyline-gondola.webp"
        }
      ]
    }
  },
  computed: {
    isLoggedIn() {
      const token = localStorage.getItem('token');
      return token && token.length > 0;
    },
    userName() {
      return localStorage.getItem('userName') || 'User'
    },
    authToken() {
      return localStorage.getItem('token');
    },
    totalAttractions() {
      return this.itinerary.reduce((total, day) => total + day.attractions.length, 0);
    },
    minBudget() {
      if (!this.itinerary.length) return 0;
      return Math.min(...this.itinerary.flatMap(day => 
        day.attractions.map(a => a.price_range[0])
      ));
    },
    maxBudget() {
      if (!this.itinerary.length) return 0;
      return Math.max(...this.itinerary.flatMap(day => 
        day.attractions.map(a => a.price_range[1])
      ));
    }
  },
  async mounted() {
    try {
      await this.loadUserPreferences();
    } catch (error) {
      console.error('Error during component initialization:', error);
      this.error = 'Failed to initialize the page. Please try refreshing.';
    }
  },

  beforeDestroy() {
    if (this.map) {
      this.map.remove();
      this.map = null;
    }
  },
  methods: {
    toggleAdvanced() {
      this.showAdvanced = !this.showAdvanced;
    },

    validateDuration() {
      this.durationWarning = '';
      const duration = this.preferences.duration;
      
      if (duration > 14) {
        this.durationWarning = 'Consider exploring multiple destinations for longer trips, or expand your travel radius for more options.';
      } else if (duration > 7) {
        this.durationWarning = 'For extended stays, you might want to increase your travel distance to discover more attractions.';
      }
    },

    async getRecommendations() {
      try {
        this.loading = true;
        this.error = null;
        this.recommendations = [];
        this.itinerary = [];

        const controller = new AbortController();
        const timeoutId = setTimeout(() => controller.abort(), 15000);

        // Calculate attractions per day (minimum 2, maximum 4)
        const attractionsPerDay = Math.min(Math.max(Math.floor(10 / this.preferences.duration), 2), 4);
        const totalAttractions = attractionsPerDay * this.preferences.duration;

        const requestBody = {
          user_id: this.getUserId(),
          preferences: {
            activity_types: this.preferences.activity_types,
            budget_range: this.preferences.budget_range,
            travel_style: this.preferences.travel_style,
            difficulty_preference: this.preferences.difficulty_preference,
            group_size: this.preferences.group_size,
            duration: this.preferences.duration,
            max_travel_distance: this.preferences.max_travel_distance
          },
          current_location: {
            lat: this.location.lat,
            lng: this.location.lng,
            address: this.location.address
          },
          top_k: Math.max(totalAttractions, 8)
        };

        console.log('Sending request:', requestBody);
        
        const response = await fetch(`${API_BASE_URL}/api/recommendations`, {
          signal: controller.signal,
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Accept': 'application/json'
          },
          body: JSON.stringify(requestBody)
        });

        clearTimeout(timeoutId);

        let data;
        try {
          data = await response.json();
          console.log('Received response:', data);
        } catch (error) {
          console.error('Failed to parse response:', error);
          throw new Error('Invalid server response');
        }

        if (!response.ok) {
          throw new Error(data.detail || 'Failed to get recommendations');
        }

        if (!data.recommendations || !Array.isArray(data.recommendations)) {
          console.error('Invalid response format:', data);
          throw new Error('Invalid response format from server');
        }

        this.recommendations = data.recommendations.map(rec => ({
          id: rec.id || rec.attraction_id,
          name: rec.name,
          description: rec.description || '',
          category: rec.category || rec.categories?.[0] || 'general',
          rating: rec.rating || 4.0,
          confidence_score: rec.confidence_score || 0.5,
          price_range: rec.price_range || [0, 100],
          location: rec.location || { lat: this.location.lat, lng: this.location.lng },
          reasons: rec.reasons || ['Based on your preferences'],
          distance: rec.distance,
          estimated_time: rec.estimated_time || '2-3 hours'
        }));

        if (this.recommendations.length === 0) {
          this.error = 'No recommendations found within your travel distance. Try increasing your travel radius in More Options.';
        } else {
          // Generate itinerary
          this.generateItinerary();
          // Get weather information
          await this.getWeatherInfo();
        }

      } catch (err) {
        console.error('Recommendation error:', err);
        if (err.name === 'AbortError') {
          this.error = 'Request timed out. Please try again.';
        } else {
          this.error = err.message || 'Failed to get recommendations. Please try again.';
        }
        this.recommendations = [];
      } finally {
        this.loading = false;
        
        if (this.recommendations.length > 0) {
          await this.$nextTick();
          await this.initMap();
        }
      }
    },

    generateItinerary() {
      const duration = this.preferences.duration;
      const attractions = [...this.recommendations];
      
      // Sort attractions by rating and confidence score
      attractions.sort((a, b) => (b.rating * b.confidence_score) - (a.rating * a.confidence_score));
      
      // Calculate attractions per day
      const attractionsPerDay = Math.max(Math.floor(attractions.length / duration), 1);
      const extraAttractions = attractions.length % duration;
      
      this.itinerary = [];
      let currentIndex = 0;
      
      for (let day = 0; day < duration; day++) {
        const dayAttractions = attractionsPerDay + (day < extraAttractions ? 1 : 0);
        const dayItems = attractions.slice(currentIndex, currentIndex + dayAttractions);
        
        // Only add days that have attractions
        if (dayItems.length > 0) {
          this.itinerary.push({
            day: day + 1,
            attractions: dayItems
          });
        }
        
        currentIndex += dayAttractions;
      }
    },

    async getWeatherInfo() {
      // Simulate weather data (in real app, you would call a weather API)
      const weatherConditions = ['sunny', 'cloudy', 'partly-cloudy', 'rainy'];
      const randomCondition = weatherConditions[Math.floor(Math.random() * weatherConditions.length)];
      
      // Simulate temperature based on location (New Zealand typical range)
      let baseTemp = 18;
      if (this.location.address.includes('Wellington')) baseTemp = 16;
      if (this.location.address.includes('Auckland')) baseTemp = 20;
      if (this.location.address.includes('Christchurch')) baseTemp = 15;
      if (this.location.address.includes('Hamilton')) baseTemp = 18;
      
      const temperature = baseTemp + Math.floor(Math.random() * 8) - 4; // ±4 degrees variation
      
      this.weatherInfo = {
        condition: randomCondition,
        temperature: temperature,
        suitable_for_outdoor: temperature > 10 && randomCondition !== 'rainy',
        location: this.location.address
      };
    },

    async savePreferences() {
      localStorage.setItem('userPreferences', JSON.stringify(this.preferences))
      alert('Preferences saved!')
    },

    async loadUserPreferences() {
      const saved = localStorage.getItem('userPreferences')
      if (saved) {
        this.preferences = { ...this.preferences, ...JSON.parse(saved) }
      }
    },



    async initMap() {
      if (this.map) {
        this.map.remove();
        this.map = null;
        this.mapInitialized = false;
      }

      if (!this.recommendations || this.recommendations.length === 0) {
        return;
      }

      for (let attempt = 1; attempt <= 3; attempt++) {
        await this.$nextTick();
        await new Promise(resolve => setTimeout(resolve, attempt * 200));

        const mapContainer = this.$refs.mapContainer;
        if (!mapContainer || mapContainer.offsetWidth === 0) {
          if (attempt === 3) return;
          continue;
        }

        try {
          const centerLat = Number(this.location?.lat) || -41.3;
          const centerLng = Number(this.location?.lng) || 174.8;

          this.map = L.map(mapContainer, {
            center: [centerLat, centerLng],
            zoom: 8,
            attributionControl: true
          });

          L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
            attribution: '© OpenStreetMap contributors',
            maxZoom: 19
          }).addTo(this.map);

          // Add destination marker
          const destinationMarker = L.marker([centerLat, centerLng], {
            title: 'Your Destination'
          }).addTo(this.map);
          destinationMarker.bindPopup('<strong>Your Destination</strong><br>' + this.location.address);

          // Add attraction markers
          const bounds = L.latLngBounds();
          bounds.extend([centerLat, centerLng]);

          this.recommendations.forEach((rec, index) => {
            if (rec.location?.lat && rec.location?.lng) {
              const lat = Number(rec.location.lat);
              const lng = Number(rec.location.lng);
              
              if (!isNaN(lat) && !isNaN(lng)) {
                // Different color for different days in itinerary
                const dayIndex = this.getAttractionDay(rec.id);
                const colors = ['red', 'blue', 'green', 'orange', 'purple', 'darkred', 'lightred'];
                const color = colors[dayIndex % colors.length] || 'gray';
                
                const marker = L.marker([lat, lng], {
                  title: rec.name,
                  icon: L.divIcon({
                    className: 'custom-div-icon',
                    html: `<div style="background-color:${color};color:white;border-radius:50%;width:25px;height:25px;text-align:center;line-height:25px;font-size:12px;font-weight:bold;">${dayIndex + 1}</div>`,
                    iconSize: [25, 25],
                    iconAnchor: [12, 12]
                  })
                }).addTo(this.map);

                marker.bindPopup(`
                  <strong>${rec.name}</strong><br>
                  ${rec.description || ''}<br>
                  Rating: ${rec.rating}<br>
                  Day: ${dayIndex + 1}
                `);

                bounds.extend([lat, lng]);
              }
            }
          });

          if (bounds.isValid()) {
            this.map.fitBounds(bounds, { padding: [20, 20] });
          }

          this.map.invalidateSize();
          this.mapInitialized = true;
          return;

        } catch (error) {
          console.error(`Error initializing map on attempt ${attempt}:`, error);
          if (this.map) {
            this.map.remove();
            this.map = null;
          }
        }
      }
    },

    getAttractionDay(attractionId) {
      for (let i = 0; i < this.itinerary.length; i++) {
        const day = this.itinerary[i];
        if (day.attractions.some(a => a.id === attractionId)) {
          return i;
        }
      }
      return 0;
    },

    updateLocation() {
      const selectedLocation = this.locations[this.location.address];
      if (selectedLocation) {
        this.location.lat = selectedLocation.lat;
        this.location.lng = selectedLocation.lng;
      }
    },

    getUserId() {
      let userId = localStorage.getItem('userId')
      if (!userId) {
        userId = 'user_' + Math.random().toString(36).substr(2, 9)
        localStorage.setItem('userId', userId)
      }
      return userId
    }
  }
}
</script>

<style scoped>
.card {
  border-radius: 8px;
}

.form-check-inline {
  margin-right: 0.5rem;
  margin-bottom: 0.25rem;
}

.sticky-top {
  top: 1rem;
}

.accordion-button:not(.collapsed) {
  background-color: #f8f9fa;
}

.custom-div-icon {
  background: transparent;
  border: none;
}
</style>
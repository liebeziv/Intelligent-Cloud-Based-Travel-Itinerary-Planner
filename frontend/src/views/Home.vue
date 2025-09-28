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
                <option v-for="option in locationOptions" :key="option.label" :value="option.label">{{ option.label }}</option>
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
                  <option v-for="option in locationOptions" :key="option.label" :value="option.label">{{ option.label }}</option>
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
            <button v-if="isLoggedIn && itinerary.length" @click="saveCurrentTrip" type="button" class="btn btn-success btn-sm ms-2">
              Save Trip
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
      <h4 class="mb-3">Your {{ summary ? summary.total_days : preferences.duration }}-Day Itinerary</h4>
      
      <div class="row">
        <div class="col-lg-8">
          <div class="accordion" id="itineraryAccordion">
            <div class="accordion-item" v-for="day in itinerary" :key="day.day_index">
              <h2 class="accordion-header">
                <button class="accordion-button" :class="{ collapsed: day.day_index !== 1 }" type="button"
                        data-bs-toggle="collapse" :data-bs-target="`#day${day.day_index}`">
                  <strong>Day {{ day.day_index }} - {{ formatDate(day.date) }}</strong>
                  <span class="ms-2 text-muted">{{ day.segments.length }} stops - {{ day.total_distance_km }} km</span>
                </button>
              </h2>
              <div :id="`day${day.day_index}`" class="accordion-collapse collapse" :class="{ show: day.day_index === 1 }"
                   data-bs-parent="#itineraryAccordion">
                <div class="accordion-body">
                  <div class="list-group">
                    <div class="list-group-item" v-for="segment in day.segments" :key="segment.attraction.id">
                      <div class="d-flex justify-content-between align-items-start">
                        <div>
                          <h6 class="mb-1">{{ segment.attraction.name }}</h6>
                          <p class="mb-1 text-muted">{{ segment.attraction.description }}</p>
                          <div class="small text-secondary">
                            Arrival {{ formatTime(segment.arrival_time) }} - {{ formatTravel(segment.travel) }}
                          </div>
                        </div>
                        <span class="badge bg-primary align-self-start">{{ segment.attraction.category }}</span>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <div class="col-lg-4">
          <div class="card mb-3">
            <div class="card-body">
              <h5 class="card-title">Trip Summary</h5>
              <ul class="list-unstyled mb-0">
                <li><strong>Total attractions:</strong> {{ totalAttractions }}</li>
                <li><strong>Total distance:</strong> {{ summary ? summary.total_distance_km : 0 }} km</li>
                <li><strong>Total travel time:</strong> {{ summary ? Math.round(summary.total_travel_time_minutes) : 0 }} min</li>
                <li><strong>Budget range:</strong> {{ minBudget }} - {{ maxBudget }} NZD</li>
              </ul>
            </div>
          </div>

          <div class="card" v-if="weatherInfo">
            <div class="card-body">
              <h5 class="card-title">Current Weather - {{ location.address }}</h5>
              <div class="d-flex align-items-center">
                <div class="display-6 me-3">{{ weatherInfo.temperature }}&deg;C</div>
                <div>
                  <div class="fw-bold text-capitalize">{{ weatherInfo.description || weatherInfo.condition }}</div>
                  <div class="small text-muted">Wind {{ weatherInfo.wind_speed }} m/s - Humidity {{ weatherInfo.humidity }}%</div>
                  <div class="small" :class="weatherInfo.suitable_for_outdoor ? 'text-success' : 'text-warning'">
                    {{ weatherInfo.suitable_for_outdoor ? 'Great for outdoor activities' : 'Consider indoor alternatives' }}
                  </div>
                </div>
              </div>
            </div>
          </div>

          <div class="card" v-if="itinerary.length">
            <div class="card-body">
              <h5 class="card-title">Route Map</h5>
              <div class="map-wrapper"><div id="map"></div></div>
            </div>
          </div>
        </div>
        </div>
      </div>
    </div>
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
                <span class="badge bg-warning text-dark" v-if="rec.rating">⭐{{ rec.rating }}</span>
              </div>

              <div class="small text-muted mb-2" v-if="rec.price_range">
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
        <div class="col-md-4 mb-3" v-for="attraction in featuredAttractions" :key="attraction.id">
          <div class="card">
            <img :src="attraction.image" class="card-img-top" style="height: 150px; object-fit: cover;" :alt="attraction.name">
            <div class="card-body p-3">
              <h6 class="card-title">{{ attraction.name }}</h6>
              <p class="card-text small">{{ attraction.description }}</p>
              <div>
                <span class="badge bg-primary me-1">{{ attraction.category }}</span>
                <span class="badge bg-warning text-dark" v-if="attraction.rating">⭐{{ attraction.rating }}</span>
              </div>
              <div class="small text-muted mt-2" v-if="attraction.price_range">
                Price: ${{ attraction.price_range[0] }} - ${{ attraction.price_range[1] }}
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
</template>

<script>
import L from 'leaflet'
import { itineraryAPI, attractionsAPI } from '../services/api'

export default {
  name: 'Home',
  data() {
    return {
      loading: false,
      error: null,
      recommendations: [],
      itinerary: [],
      summary: null,
      map: null,
      mapInitialized: false,
      showAdvanced: false,
      durationWarning: '',
      weatherInfo: null,
      authState: {
        token: localStorage.getItem('token') || '',
        name: localStorage.getItem('userName') || '',
        email: localStorage.getItem('userEmail') || ''
      },
      activityOptions: ['natural', 'scenic', 'adventure', 'cultural', 'family', 'historical'],
      preferences: {
        activity_types: ['natural', 'scenic'],
        budget_range: [100, 400],
        travel_style: 'adventure',
        difficulty_preference: 'medium',
        max_travel_distance: 150,
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
      defaultLocationOptions: [
        { label: 'Auckland, New Zealand', lat: -36.8485, lng: 174.7633 },
        { label: 'Bay of Islands, New Zealand', lat: -35.2, lng: 174.1 },
        { label: 'Christchurch, New Zealand', lat: -43.532, lng: 172.6306 },
        { label: 'Fiordland, New Zealand', lat: -44.6, lng: 167.9 },
        { label: 'Franz Josef, New Zealand', lat: -43.4, lng: 170.2 },
        { label: 'Hamilton, New Zealand', lat: -37.787, lng: 175.2793 },
        { label: 'Nelson, New Zealand', lat: -41.2706, lng: 173.284 },
        { label: 'Queenstown, New Zealand', lat: -45.0312, lng: 168.6626 },
        { label: 'Rotorua, New Zealand', lat: -38.1368, lng: 176.2497 },
        { label: 'Waitomo, New Zealand', lat: -38.2607, lng: 175.1102 },
        { label: 'Wellington, New Zealand', lat: -41.3, lng: 174.8 }
      ],
      locationOptions: [],
      locationLookup: {},
      savedItineraries: [],
      featuredAttractions: [],
      fallbackFeaturedAttractions: [
        {
          id: 'AKL_SKY_TOWER',
          name: 'Sky Tower',
                  description: "Panoramic city views from New Zealand's tallest tower.",
          category: 'urban',
          rating: 4.7,
          price_range: [35, 85],
          image: '/images/skyline-gondola.webp',
          region: 'Auckland',
          location: { lat: -36.8485, lng: 174.7633 }
        },
        {
          id: 'WLG_TE_PAPA',
          name: 'Te Papa Museum',
          description: "Interactive national museum exploring culture and history.",
          category: 'cultural',
          rating: 4.6,
          price_range: [0, 40],
          image: '/images/milford-sound.webp',
          region: 'Wellington',
          location: { lat: -41.2905, lng: 174.7821 }
        },
        {
          id: 'ROT_TE_PUIA',
          name: 'Te Puia Geothermal Valley',
          description: "Pohutu geyser eruptions and cultural experiences.",
          category: 'natural',
          rating: 4.5,
          price_range: [110, 210],
          image: '/images/skyline-gondola.webp',
          region: 'Rotorua',
          location: { lat: -38.144, lng: 176.2502 }
        },
        {
          id: 'CHC_BOTANIC',
          name: 'Christchurch Botanic Gardens',
          description: "Riverside gardens and conservatories in the city centre.",
          category: 'natural',
          rating: 4.7,
          price_range: [0, 20],
          image: '/images/milford-sound.webp',
          region: 'Christchurch',
          location: { lat: -43.5309, lng: 172.6271 }
        },
        {
          id: 'ZQN_SKYLINE',
          name: 'Queenstown Skyline Gondola',
          description: "Gondola ride with luge tracks and mountain vistas.",
          category: 'adventure',
          rating: 4.6,
          price_range: [95, 180],
          image: '/images/skyline-gondola.webp',
          region: 'Queenstown',
          location: { lat: -45.0312, lng: 168.6626 }
        },
        {
          id: 'WKO_HOBBITON',
          name: 'Hobbiton Movie Set',
          description: "Guided tour through the Shire film set and Green Dragon Inn.",
          category: 'cultural',
          rating: 4.8,
          price_range: [150, 260],
          image: '/images/milford-sound.webp',
          region: 'Waikato',
          location: { lat: -37.8722, lng: 175.6823 }
        }
      ],
      fallbackAttractionImages: {
        'AKL_SKY_TOWER': '/images/skyline-gondola.webp',
        'WLG_TE_PAPA': '/images/milford-sound.webp',
        'ROT_TE_PUIA': '/images/skyline-gondola.webp',
        'CHC_BOTANIC': '/images/milford-sound.webp',
        'ZQN_SKYLINE': '/images/skyline-gondola.webp',
        'WKO_HOBBITON': '/images/milford-sound.webp'
      }
    }
  },
  computed: {
    isLoggedIn() {
      return !!this.authState.token
    },
    userName() {
      return localStorage.getItem('userName') || 'User'
    },
    totalAttractions() {
      return this.itinerary.reduce((total, day) => total + ((day.segments && day.segments.length) || 0), 0)
    },
    minBudget() {
      const prices = []
      this.itinerary.forEach(day => {
        (day.segments || []).forEach(segment => {
          const range = segment.attraction?.price_range
          if (range && range.length) {
            prices.push(range[0])
          }
        })
      })
      return prices.length ? Math.min(...prices) : 0
    },
    maxBudget() {
      const prices = []
      this.itinerary.forEach(day => {
        (day.segments || []).forEach(segment => {
          const range = segment.attraction?.price_range
          if (range && range.length) {
            prices.push(range[1])
          }
        })
      })
      return prices.length ? Math.max(...prices) : 0
    }
  },
  async mounted() {
    this.mergeLocationOptions(this.defaultLocationOptions, true)
    try {
      await Promise.all([
        this.loadUserPreferences(),
        this.fetchFeaturedAttractions()
      ])
      this.updateLocation()
    } catch (error) {
      console.error('Error during component initialization:', error)
      this.error = 'Failed to initialize the page. Please try refreshing.'
      this.featuredAttractions = this.fallbackFeaturedAttractions.map(this.normalizeAttraction)
      this.mergeLocationOptions(this.extractLocationsFromAttractions(this.fallbackFeaturedAttractions))
    }
  },
  beforeUnmount() {
    window.removeEventListener('auth-changed', this.syncAuthState)
    window.removeEventListener('storage', this.syncAuthState)
    if (this.map) {
      this.map.remove()
      this.map = null
    }
  },
  methods: {
    mergeLocationOptions(options, reset = false) {
      const newLookup = reset ? {} : { ...this.locationLookup }
      const newList = reset ? [] : [...this.locationOptions]

      if (Array.isArray(options)) {
        options.forEach(option => {
          if (!option) {
            return
          }
          const label = String(option.label || option.address || '').trim()
          const lat = Number(option.lat ?? option.latitude)
          const lng = Number(option.lng ?? option.longitude)
          if (!label || Number.isNaN(lat) || Number.isNaN(lng)) {
            return
          }
          if (!newLookup[label]) {
            newLookup[label] = { lat, lng }
            newList.push({ label, lat, lng })
          }
        })
      }

      if (!newList.length) {
        return
      }

      newList.sort((a, b) => a.label.localeCompare(b.label))
      this.locationLookup = newLookup
      this.locationOptions = newList

      const current = newLookup[this.location.address]
      if (current) {
        this.location.lat = current.lat
        this.location.lng = current.lng
      } else {
        const first = newList[0]
        this.location.address = first.label
        this.location.lat = first.lat
        this.location.lng = first.lng
      }
    },

    extractLocationsFromAttractions(attractions = []) {
      if (!Array.isArray(attractions)) {
        return []
      }
      return attractions
        .map(item => {
          if (!item) {
            return null
          }
          const location = item.location || {}
          const lat = Number(location.lat ?? location.latitude)
          const lng = Number(location.lng ?? location.longitude)
          if (Number.isNaN(lat) || Number.isNaN(lng)) {
            return null
          }
          const region = (item.region || '').toString().trim()
          const labelBase = region || item.name
          if (!labelBase) {
            return null
          }
          return { label: `${labelBase}, New Zealand`, lat, lng }
        })
        .filter(Boolean)
    },

    extractLocationsFromItinerary(days = []) {
      if (!Array.isArray(days)) {
        return []
      }
      const attractions = []
      days.forEach(day => {
        (day?.segments || []).forEach(segment => {
          const attraction = segment?.attraction
          if (!attraction) {
            return
          }
          attractions.push({
            name: attraction.name,
            region: attraction.region || day?.region || '',
            location: attraction.location
          })
        })
      })
      return this.extractLocationsFromAttractions(attractions)
    },

    syncAuthState() {
      this.authState = {
        token: localStorage.getItem('token') || '',
        name: localStorage.getItem('userName') || '',
        email: localStorage.getItem('userEmail') || ''
      }
    },

    async fetchFeaturedAttractions() {
      try {
        const response = await attractionsAPI.getAll({ limit: 24 })
        const payload = Array.isArray(response.data) ? response.data : []
        if (payload.length) {
          this.featuredAttractions = payload.map(item => this.normalizeAttraction(item))
          this.mergeLocationOptions(this.extractLocationsFromAttractions(payload))
          return
        }
      } catch (error) {
        console.error('Failed to load attractions', error)
      }
      this.featuredAttractions = this.fallbackFeaturedAttractions.map(item => this.normalizeAttraction(item))
      this.mergeLocationOptions(this.extractLocationsFromAttractions(this.fallbackFeaturedAttractions))
    },

    normalizeAttraction(attraction) {
      if (!attraction) {
        return {}
      }
      const categories = attraction.categories || []
      const ratingSource = typeof attraction.rating === 'number'
        ? attraction.rating
        : (attraction.rating && (attraction.rating.average ?? attraction.rating.avg))
      let rating = null
      if (ratingSource !== null && ratingSource !== undefined) {
        const numeric = Number(ratingSource)
        rating = Number.isNaN(numeric) ? null : Number(numeric.toFixed(1))
      }
      const priceRange = attraction.price_range || attraction.priceRange || [120, 260]
      const image = attraction.image || attraction.image_url || attraction.imageUrl || this.fallbackAttractionImages[attraction.id] || '/images/milford-sound.webp'
      return {
        id: attraction.id,
        name: attraction.name,
        description: attraction.description || '',
        category: attraction.category || categories[0] || 'experience',
        rating,
        price_range: priceRange,
        image
      }
    },

    toggleAdvanced() {
      this.showAdvanced = !this.showAdvanced
    },

    validateDuration() {
      this.durationWarning = ''
      const duration = this.preferences.duration
      if (duration > 14) {
        this.durationWarning = 'Consider exploring multiple destinations for longer trips, or expand your travel radius for more options.'
      } else if (duration > 7) {
        this.durationWarning = 'For extended stays, you might want to increase your travel distance to discover more attractions.'
      }
    },

    async getRecommendations() {
      try {
        this.loading = true
        this.error = null
        this.recommendations = []
        this.itinerary = []
        this.summary = null

        const payload = {
          destination: this.location.address,
          start_date: new Date().toISOString().split('T')[0], // today's date
          end_date: new Date(Date.now() + this.preferences.duration * 24 * 60 * 60 * 1000).toISOString().split('T')[0], // end date
          budget: this.preferences.budget_range[1], // use max budget
          travelers: this.preferences.group_size || 1,
          preferences: {
            activities: this.preferences.activity_types,
            pace: "moderate"
        },
        accommodation_type: "hotel",
        transport_mode: "public"
      }

        const response = await itineraryAPI.plan(payload)
        const data = response.data ?? response

        this.recommendations = data.recommendations || []
        this.itinerary = data.days || []
        this.summary = data.summary || null
        this.weatherInfo = data.weather || null
        const dynamicLocations = [
          ...this.extractLocationsFromAttractions(this.recommendations),
          ...this.extractLocationsFromItinerary(this.itinerary)
        ]
        if (dynamicLocations.length) {
          this.mergeLocationOptions(dynamicLocations)
        }

        if (!this.itinerary.length) {
          const contextMessage = typeof data.context === 'string'
            ? data.context
            : (data.context && data.context.message)
          this.error = contextMessage || 'No itinerary could be generated with the current preferences.'
        }
      } catch (err) {
        console.error('Itinerary planning error:', err)
        const detail = err?.response?.data?.detail
        this.error = detail || err.message || 'Failed to plan itinerary. Please try again.'
      } finally {
        this.loading = false
        if (this.itinerary.length) {
          await this.$nextTick()
          await this.initMap()
        }
      }
    },

    async savePreferences() {
      localStorage.setItem('userPreferences', JSON.stringify(this.preferences))
      alert('Preferences saved!')
    },

    async saveCurrentTrip() {
      if (!this.itinerary.length) {
        alert('Please generate an itinerary before saving.')
        return
      }

      if (!this.isLoggedIn) {
        this.saveTripLocally()
        return
      }

      const payload = {
        title: `${this.location.address} (${this.preferences.duration} days)`,
        items: this.itinerary,
        metadata: {
          location: this.location,
          preferences: this.preferences,
          summary: this.summary
        }
      }

      try {
        await itineraryAPI.create(payload)
        alert('Trip saved to your account!')
      } catch (error) {
        console.error('Failed to save trip on server', error)
        this.saveTripLocally(false)
        alert('Server save failed, trip stored locally instead.')
      }
    },

    saveTripLocally(showAlert = true) {
      const userId = this.getUserId()
      const key = `trips_${userId}`
      const existing = localStorage.getItem(key)
      const trips = existing ? JSON.parse(existing) : []
      const trip = {
        id: `trip_${Date.now()}`
        ,
        created_at: new Date().toISOString(),
        preferences: { ...this.preferences },
        location: { ...this.location },
        itinerary: this.itinerary,
        summary: this.summary
      }
      trips.unshift(trip)
      localStorage.setItem(key, JSON.stringify(trips))
      if (showAlert) {
        alert('Trip saved locally! View it on your user page.')
      }
    },

    async loadUserPreferences() {
      const saved = localStorage.getItem('userPreferences')
      if (saved) {
        this.preferences = { ...this.preferences, ...JSON.parse(saved) }
      }
      this.updateLocation()
    },

    async initMap() {
      if (!this.itinerary.length) {
        return
      }

      if (this.map) {
        this.map.remove()
        this.map = null
        this.mapInitialized = false
      }

      const mapElement = document.getElementById('map')
      if (!mapElement) {
        console.warn('Map container not found')
        return
      }

      const centerLat = Number(this.location?.lat) || -41.3
      const centerLng = Number(this.location?.lng) || 174.8

      this.map = L.map(mapElement, {
        center: [centerLat, centerLng],
        zoom: 8,
        attributionControl: true
      })

      this.map.whenReady(() => {
        requestAnimationFrame(() => this.map.invalidateSize())
      })

      L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: 'OpenStreetMap contributors',
        maxZoom: 19
      }).addTo(this.map)

      const bounds = L.latLngBounds()
      bounds.extend([centerLat, centerLng])

      const colors = ['#d62828', '#1d3557', '#2a9d8f', '#f4a261', '#6a4c93', '#457b9d', '#ffb703']

      this.itinerary.forEach(day => {
        const dayColor = colors[(day.day_index - 1) % colors.length]
        const polylinePoints = []

        ;(day.segments || []).forEach(segment => {
          const location = segment.attraction?.location || {}
          const lat = Number(location.lat)
          const lng = Number(location.lng)
          if (Number.isNaN(lat) || Number.isNaN(lng)) {
            return
          }

          polylinePoints.push([lat, lng])
          bounds.extend([lat, lng])

          const marker = L.marker([lat, lng], {
            title: segment.attraction.name,
            icon: L.divIcon({
              className: 'custom-div-icon',
              html: `<div style="background-color:${dayColor};color:white;border-radius:50%;width:28px;height:28px;text-align:center;line-height:28px;font-size:12px;font-weight:bold;">${day.day_index}</div>`,
              iconSize: [28, 28],
              iconAnchor: [14, 14]
            })
          }).addTo(this.map)

          const travelInfo = segment.travel && segment.travel.distance_km != null
            ? `Travel: ${segment.travel.distance_km} km - ${segment.travel.duration_minutes} min<br>`
            : ''

          marker.bindPopup(`
            <strong>${segment.attraction.name}</strong><br>
            Arrival: ${this.formatTime(segment.arrival_time)}<br>
            ${travelInfo}
            ${segment.attraction.description || ''}
          `)
        })

        if (polylinePoints.length > 1) {
          L.polyline(polylinePoints, { color: dayColor, weight: 3, opacity: 0.7 }).addTo(this.map)
        }
      })

      if (bounds.isValid()) {
        this.map.fitBounds(bounds, { padding: [20, 20] })
      }

      requestAnimationFrame(() => this.map.invalidateSize())
      this.mapInitialized = true
    },

    formatDate(dateString) {
      if (!dateString) return 'N/A'
      const date = new Date(dateString)
      return date.toLocaleDateString('en-NZ', { month: 'short', day: 'numeric', year: 'numeric' })
    },

    formatTime(dateString) {
      if (!dateString) return 'N/A'
      const date = new Date(dateString)
      return date.toLocaleTimeString('en-NZ', { hour: '2-digit', minute: '2-digit' })
    },

    formatTravel(travel) {
      if (!travel || travel.distance_km == null) {
        return 'N/A'
      }
      return `${travel.distance_km} km - ${travel.duration_minutes} min`
    },

    updateLocation() {
      const selectedLocation = this.locationLookup[this.location.address]
      if (selectedLocation) {
        this.location.lat = selectedLocation.lat
        this.location.lng = selectedLocation.lng
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
.map-wrapper {
  height: 320px;
  border-radius: 12px;
  overflow: hidden;
}

#map {
  width: 100%;
  height: 100%;
}


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




























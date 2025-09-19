<template>
  <div class="container mt-4">
    
    <div class="text-center mb-4">
      <h2>AI-Powered Travel Recommendations</h2>
      <p class="text-muted">Get personalized suggestions for your New Zealand adventure</p>
    </div>

    
    <div class="card mb-4">
      <div class="card-body">
        <h5 class="card-title">Your Preferences</h5>
        <form @submit.prevent="getRecommendations">
          <div class="row">
            
            <div class="col-md-4 mb-3">
              <label class="form-label">Activity Types</label>
              <div style="max-height: 120px; overflow-y: auto; border: 1px solid #dee2e6; border-radius: 4px; padding: 8px;">
                <div class="form-check form-check-inline" v-for="activity in activityOptions" :key="activity">
                  <input 
                    class="form-check-input" 
                    type="checkbox" 
                    :id="activity" 
                    :value="activity"
                    v-model="preferences.activity_types"
                  >
                  <label class="form-check-label" :for="activity" style="font-size: 0.9em;">
                    {{ activity }}
                  </label>
                </div>
              </div>
            </div>
            
           
            <div class="col-md-4 mb-3">
              <label class="form-label">Budget (NZD)</label>
              <div class="input-group input-group-sm">
                <input v-model.number="preferences.budget_range[0]" type="number" class="form-control" placeholder="Min">
                <span class="input-group-text">-</span>
                <input v-model.number="preferences.budget_range[1]" type="number" class="form-control" placeholder="Max">
              </div>
              
              <label class="form-label mt-2">Travel Style</label>
              <select v-model="preferences.travel_style" class="form-control form-control-sm">
                <option value="adventure">Adventure</option>
                <option value="relaxing">Relaxing</option>
                <option value="cultural">Cultural</option>
                <option value="family">Family</option>
              </select>
            </div>

            <div class="col-md-4 mb-3">
              <label class="form-label">Group Size</label>
              <input v-model.number="preferences.group_size" type="number" min="1" class="form-control form-control-sm">
              
              <label class="form-label mt-2">Duration (days)</label>
              <input v-model.number="preferences.duration" type="number" min="1" class="form-control form-control-sm">
              
              <label class="form-label mt-2">Location</label>
              <input v-model="location.address" type="text" class="form-control form-control-sm" placeholder="Wellington, NZ">
            </div>
          </div>

          <div class="text-center">
            <button type="submit" class="btn btn-primary me-2" :disabled="loading">
              {{ loading ? 'Loading...' : 'Get Recommendations' }}
            </button>
            <button v-if="isLoggedIn" @click="savePreferences" type="button" class="btn btn-outline-secondary btn-sm">
              Save Preferences
            </button>
          </div>
        </form>
      </div>
    </div>

    
    <div v-if="loading" class="text-center py-4">
      <div class="spinner-border" role="status"></div>
      <p class="mt-2">Finding recommendations...</p>
    </div>

    
    <div v-if="error" class="alert alert-danger">
      {{ error }}
      <button type="button" class="btn-close float-end" @click="error = null"></button>
    </div>

    
    <div v-if="recommendations.length && !loading">
      <h4 class="mb-3">Recommended for You</h4>
      
      <div class="row">
        <div class="col-lg-8">
          <div class="row">
            <div class="col-md-6 mb-3" v-for="rec in recommendations" :key="rec.id">
              <div class="card h-100">
                <div class="card-body">
                  <h6 class="card-title">{{ rec.name }}</h6>
                  <p class="card-text small">{{ rec.description }}</p>
                  
                  <div class="d-flex justify-content-between align-items-center mb-2">
                    <span class="badge bg-primary">{{ rec.category }}</span>
                    <span class="badge bg-warning text-dark">★ {{ rec.rating }}</span>
                  </div>

                  <div class="mb-2">
                    <small>Match: {{ Math.round(rec.confidence_score * 100) }}%</small>
                    <div class="progress" style="height: 6px;">
                      <div class="progress-bar" :style="{ width: (rec.confidence_score * 100) + '%' }"></div>
                    </div>
                  </div>

                  <div class="small text-muted mb-2">
                    Price: ${{ rec.price_range[0] }} - ${{ rec.price_range[1] }}
                  </div>

                  <div v-if="rec.reasons && rec.reasons.length" class="small">
                    <strong>Why:</strong>
                    <ul class="mb-1" style="padding-left: 1rem;">
                      <li v-for="reason in rec.reasons.slice(0,2)" :key="reason">{{ reason }}</li>
                    </ul>
                  </div>
                </div>
                
                <div class="card-footer p-2" v-if="isLoggedIn">
                  <button @click="saveToItinerary(rec)" class="btn btn-outline-primary btn-sm w-100">
                    Save to Itinerary
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
        
        
        <div class="col-lg-4">
          <div class="card">
            <div class="card-header">
              <h6 class="mb-0">Locations Map</h6>
            </div>
            <div class="card-body p-0">
              <div id="map" style="height: 300px;"></div>
            </div>
          </div>
        </div>
      </div>
    </div>

    
    <div v-if="isLoggedIn && savedItineraries.length" class="mt-4">
      <h5>Your Saved Itineraries</h5>
      <div class="row">
        <div class="col-md-3 mb-2" v-for="itinerary in savedItineraries" :key="itinerary.id">
          <div class="card">
            <div class="card-body p-3">
              <h6 class="card-title">{{ itinerary.title }}</h6>
              <small class="text-muted">{{ itinerary.items?.length || 0 }} items</small>
            </div>
          </div>
        </div>
      </div>
    </div>

    
    <div v-if="!recommendations.length && !loading && !error">
      <h4>Popular Destinations</h4>
      <p class="text-muted">Set your preferences above for personalized recommendations</p>
      
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

export default {
  name: 'Home',
  data() {
    return {
      loading: false,
      error: null,
      recommendations: [],
      savedItineraries: [],
      map: null,
      activityOptions: ['natural', 'scenic', 'adventure', 'cultural', 'family', 'historical'],
      preferences: {
        activity_types: ['natural', 'scenic'],
        budget_range: [100, 400],
        travel_style: 'adventure',
        group_size: 2,
        duration: 7
      },
      location: {
        address: 'Wellington, New Zealand',
        lat: -41.3,
        lng: 174.8
      },
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
      return !!localStorage.getItem('token')
    },
    userName() {
      return localStorage.getItem('userName') || 'User'
    }
  },
  async mounted() {
    await this.loadUserPreferences()
    if (this.isLoggedIn) {
      await this.loadSavedItineraries()
    }
  },
  methods: {
    async getRecommendations() {
      this.loading = true
      this.error = null

      try {
        const response = await fetch('http://localhost:8000/api/recommendations/', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            user_id: this.getUserId(),
            preferences: this.preferences,
            current_location: this.location,
            top_k: 6
          })
        })

        if (!response.ok) throw new Error('Failed to get recommendations')

        const data = await response.json()
        this.recommendations = data.recommendations || []
        
        this.$nextTick(() => this.initMap())

      } catch (err) {
        this.error = 'Failed to get recommendations. Please try again.'
      } finally {
        this.loading = false
      }
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

    async saveToItinerary(recommendation) {
      try {
        const response = await fetch('http://localhost:8000/api/itineraries', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${localStorage.getItem('token')}`
          },
          body: JSON.stringify({
            title: `${recommendation.name} Visit`,
            items: [recommendation.name]
          })
        })

        if (response.ok) {
          alert('Added to itinerary!')
          await this.loadSavedItineraries()
        }
      } catch (error) {
        console.error('Failed to save:', error)
      }
    },

    async loadSavedItineraries() {
      // Implementation for loading itineraries
    },

    initMap() {
      if (this.map) this.map.remove()

      this.map = L.map('map').setView([this.location.lat, this.location.lng], 6)
      L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png').addTo(this.map)

      this.recommendations.forEach(rec => {
        if (rec.location?.lat && rec.location?.lng) {
          L.marker([rec.location.lat, rec.location.lng])
            .addTo(this.map)
            .bindPopup(`<strong>${rec.name}</strong>`)
        }
      })
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

.progress {
  height: 6px;
}
</style>
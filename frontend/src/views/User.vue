<template>
  <div class="container mt-4">
    <div class="row">
      <div class="col-lg-4 mb-3">
        <div class="card h-100">
          <div class="card-header">
            <h5 class="mb-0">Profile</h5>
          </div>
          <div class="card-body">
            <div class="d-flex align-items-center mb-3">
              <div class="rounded-circle bg-primary text-white d-flex align-items-center justify-content-center" style="width:48px;height:48px;font-weight:600;">
                {{ initials }}
              </div>
              <div class="ms-3">
                <div class="fw-bold">{{ userName || 'User' }}</div>
                <div class="text-muted small">{{ userEmail || 'Not set' }}</div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div class="col-lg-8">
        <div class="card">
          <div class="card-header d-flex align-items-center justify-content-between">
            <h5 class="mb-0">My Trips</h5>
            <button class="btn btn-sm btn-outline-danger" v-if="trips.length" @click="clearTrips">Clear All</button>
          </div>
          <div class="card-body">
            <div v-if="!trips.length" class="text-muted">No trips saved yet. Plan a trip and click Save Trip.</div>

            <div class="accordion" id="tripsAccordion" v-else>
              <div class="accordion-item" v-for="(trip, idx) in trips" :key="trip.id">
                <h2 class="accordion-header">
                  <button class="accordion-button" :class="{ collapsed: idx !== 0 }" type="button" :data-bs-toggle="'collapse'" :data-bs-target="`#trip${idx}`">
                    <strong>{{ trip.location?.address || 'Trip' }}</strong>
                    <span class="ms-2 text-muted">{{ trip.preferences?.duration }} days</span>
                  </button>
                </h2>
                <div :id="`trip${idx}`" class="accordion-collapse collapse" :class="{ show: idx === 0 }" :data-bs-parent="'#tripsAccordion'">
                  <div class="accordion-body">
                    <div class="row g-3">
                      <div class="col-md-6">
                        <div class="small text-muted">Destination</div>
                        <div>{{ trip.location?.address }}</div>
                      </div>
                      <div class="col-md-6">
                        <div class="small text-muted">Trip Duration (days)</div>
                        <div>{{ trip.preferences?.duration }}</div>
                      </div>
                      <div class="col-md-6">
                        <div class="small text-muted">Activity Types</div>
                        <div>
                          <span v-for="a in trip.preferences?.activity_types || []" :key="a" class="badge bg-primary me-1">{{ a }}</span>
                        </div>
                      </div>
                      <div class="col-md-6">
                        <div class="small text-muted">Budget (NZD)</div>
                        <div>${{ trip.preferences?.budget_range?.[0] }} - ${{ trip.preferences?.budget_range?.[1] }}</div>
                      </div>
                      <div class="col-md-6">
                        <div class="small text-muted">Travel Style</div>
                        <div class="text-capitalize">{{ trip.preferences?.travel_style }}</div>
                      </div>
                      <div class="col-md-6">
                        <div class="small text-muted">Group Size</div>
                        <div>{{ trip.preferences?.group_size }}</div>
                      </div>
                    </div>

                    <div class="mt-3 d-flex gap-2">
                      <button class="btn btn-sm btn-outline-primary" @click="reopenTrip(trip)">Open in Planner</button>
                      <button class="btn btn-sm btn-outline-danger" @click="deleteTrip(trip.id)">Delete</button>
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
  
</template>

<script>
export default {
  name: 'User',
  data() {
    return {
      trips: []
    }
  },
  computed: {
    userName() {
      return localStorage.getItem('userName') || ''
    },
    userEmail() {
      return localStorage.getItem('userEmail') || ''
    },
    initials() {
      const name = this.userName || this.userEmail || 'U'
      return name.split(' ').map(p => p[0]).join('').slice(0,2).toUpperCase()
    },
    userId() {
      return localStorage.getItem('userId') || 'guest'
    }
  },
  mounted() {
    this.loadTrips()
  },
  methods: {
    storageKey() {
      return `trips_${this.userId}`
    },
    loadTrips() {
      try {
        const raw = localStorage.getItem(this.storageKey())
        this.trips = raw ? JSON.parse(raw) : []
      } catch (e) {
        this.trips = []
      }
    },
    saveTrips() {
      localStorage.setItem(this.storageKey(), JSON.stringify(this.trips))
    },
    deleteTrip(id) {
      this.trips = this.trips.filter(t => t.id !== id)
      this.saveTrips()
    },
    clearTrips() {
      if (confirm('Delete all saved trips?')) {
        this.trips = []
        this.saveTrips()
      }
    },
    reopenTrip(trip) {
      // Store selected trip preferences and navigate home
      if (trip?.preferences) {
        localStorage.setItem('userPreferences', JSON.stringify(trip.preferences))
      }
      this.$router.push('/')
    }
  }
}
</script>

<style scoped>
.badge { font-weight: 500; }
</style>



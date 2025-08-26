<template>
  <div class="container mt-4 d-flex justify-content-center">
    <div class="planner-box">
      <h1 class="text-center">Travel Planner</h1>
      <p class="text-center">Choose your city and date, then get your itinerary!</p>

      <!-- Input form -->
      <div class="card mb-4 shadow-sm">
        <div class="card-body">
          <h5 class="card-title">New Plan</h5>
          <form @submit.prevent="generateItinerary">
            <div class="mb-3">
              <label class="form-label">City</label>
              <select v-model="plan.city" class="form-control" required>
                <option disabled value="">-- Choose a city --</option>
                <option>Queenstown</option>
                <option>Auckland</option>
                <option>Wellington</option>
                <option>Christchurch</option>
                <option>Rotorua</option>
              </select>
            </div>
            <div class="mb-3">
              <label class="form-label">Date</label>
              <input v-model="plan.date" type="date" class="form-control" required />
            </div>
            <button type="submit" class="btn btn-primary w-100">Process</button>
          </form>
        </div>
      </div>

      <!-- Output itinerary -->
      <div v-if="itinerary.length" class="mt-4">
        <h4 class="mb-3 text-center">
          Your Itinerary for {{ plan.city }} ({{ plan.date }})
        </h4>
        <ul class="mb-4 list-group">
          <li v-for="(item, index) in itinerary" :key="index" class="list-group-item">
            <strong>{{ item.time }}</strong> – {{ item.activity }} <br />
            📍 {{ item.location }} <br />
            💡 <em>{{ item.note }}</em>
          </li>
        </ul>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: "Planner",
  data() {
    return {
      plan: {
        city: "",
        date: "",
      },
      itinerary: [],
    };
  },
  methods: {
    generateItinerary() {
      // dummy data
      if (this.plan.city === "Queenstown") {
        this.itinerary = [
          {
            time: "09:00",
            activity: "Skyline Gondola & Luge",
            location: "Brecon St, Queenstown",
            note: "Great views to start your trip!",
          },
          {
            time: "13:00",
            activity: "Lunch at Fergburger",
            location: "Queenstown CBD",
            note: "Famous burger spot 🍔",
          },
          {
            time: "15:00",
            activity: "Kawarau Bridge Bungy",
            location: "State Hwy 6, Gibbston",
            note: "Thrilling adventure jump!",
          },
          {
            time: "19:00",
            activity: "Dinner by the lake",
            location: "Lake Wakatipu",
            note: "Relax with sunset view 🌅",
          },
        ];
      } else if (this.plan.city === "Auckland") {
        this.itinerary = [
          {
            time: "10:00",
            activity: "Sky Tower Visit",
            location: "Victoria St W, Auckland",
            note: "Panoramic city view",
          },
          {
            time: "12:30",
            activity: "Lunch at Viaduct Harbour",
            location: "Viaduct, Auckland",
            note: "Seafood and harbor vibes 🐟",
          },
          {
            time: "15:00",
            activity: "Auckland War Memorial Museum",
            location: "Auckland Domain",
            note: "Indoor option if it rains",
          },
          {
            time: "18:00",
            activity: "Evening stroll at Mission Bay",
            location: "Mission Bay Beach",
            note: "Perfect place to relax",
          },
        ];
      } else {
        this.itinerary = [
          {
            time: "09:00",
            activity: "City tour",
            location: this.plan.city,
            note: "Explore the highlights",
          },
        ];
      }
    },
  },
};
</script>

<style scoped>
.planner-box {
  max-width: 500px;
  width: 100%;
}
.card {
  border-radius: 0.75rem;
}
</style>

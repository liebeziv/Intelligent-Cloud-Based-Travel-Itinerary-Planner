<template>
  <div class="container mt-4">
    <h1 class="text-center">Dashboard</h1>
    <p class="text-center">Welcome to the Intelligent Travel Planner!</p>
    <div class="row justify-content-center">
      <div class="col-md-4" v-for="card in cards" :key="card.title">
        <div class="card mb-3 ">
          <div class="card-body text-center">
            <h5 class="card-title">{{ card.title }}</h5>
            <p class="card-text">{{ card.description }}</p>
            <div class="d-flex justify-content-center">
                <router-link :to="card.link" class="btn btn-primary">Open</router-link>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'Dashboard',
  data() {
    return {
      cards: [
        { title: 'Travel Plans', description: 'Create a new itinerary', link: '/planner' },
        { title: 'Popular Destinations', description: 'View recommended attractions', link: '/' },
      ],
    }
  }
}
</script>

<template>
  <div class="container mt-4">
    <h1 class="text-center">Home</h1>
    <p class="text-center">Discover the best attractions in New Zealand!</p>

    <div class="row justify-content-center">
      <div class="col-md-6 col-lg-4 mb-4" v-for="attraction in attractions" :key="attraction.id">
        <div class="card h-100">
          <img :src="attraction.image" class="card-img-top fixed-card-img" :alt="attraction.name">
          <small class="text-muted">
            <a :href="attraction.sourceUrl" target="_blank">Image source</a>
          </small>
          <div class="card-body">
            <h5 class="card-title">{{ attraction.name }}</h5>
            <p class="card-text">{{ attraction.description }}</p>
            <p><strong>Category:</strong> <span class="badge bg-primary">{{ attraction.category }}</span></p>
            <p><strong>Rating:</strong> <span class="badge bg-warning text-dark">⭐ {{ attraction.rating }}</span></p>
            <p v-if="attraction.extra"><strong>Extra Info:</strong> {{ attraction.extra }}</p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'Home',
  data() {
    return {
      attractions: [
        {
          id: 1,
          name: "Milford Sound",
          description: "Famous fiord in Fiordland National Park",
          category: "nature",
          rating: 4.8,
          image: "/images/milford-sound.webp",
          sourceUrl: "https://onlyluxe.com.au/destinations/australasia/new-zealand/milford-sound.html",
          extra: "Best visited in summer months for clear views of waterfalls."
        },
        {
          id: 2,
          name: "Queenstown Skyline Gondola",
          description: "Scenic gondola ride",
          category: "adventure",
          rating: 4.6,
          image: "/images/skyline-gondola.webp",
          sourceUrl: "https://www.newzealand.com/in/plan/business/skyline-queenstown--gondola/",
          extra: "Offers panoramic views of Lake Wakatipu and mountains."
        }
      ]
    }
  }
}
</script>

<style>
.fixed-card-img {
  width: 100%;
  height: 200px; 
  object-fit: cover;
}
</style>
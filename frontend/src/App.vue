<template>
  <div id="app">
    <nav class="navbar navbar-expand-lg navbar-dark bg-dark">
      <div class="container">
        <router-link class="navbar-brand" to="/">
          <i class="fas fa-plane me-2"></i>Travel Planner
        </router-link>

        <div class="navbar-nav ms-auto" v-if="!isLoggedIn">
          <router-link class="nav-link" to="/login">Login</router-link>
          <router-link class="nav-link" to="/register">Register</router-link>
        </div>
        
        <div class="navbar-nav ms-auto" v-else>
          <span class="navbar-text me-3">Welcome, {{ userName }}</span>
          <button @click="logout" class="btn btn-outline-light btn-sm">Logout</button>
        </div>
      </div>
    </nav>

    <router-view />
  </div>
</template>

<script>
export default {
  name: 'App',
  computed: {
    isLoggedIn() {
      return !!localStorage.getItem('token')
    },
    userName() {
      return localStorage.getItem('userName') || 'User'
    }
  },
  methods: {
    logout() {
      localStorage.removeItem('token')
      localStorage.removeItem('userName')
      this.$router.push('/')
      location.reload()
    }
  }
}
</script>

<style>
#app {
  font-family: Avenir, Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}
</style>
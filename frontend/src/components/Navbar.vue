<template>
  <nav class="navbar navbar-expand-lg navbar-dark bg-dark shadow-sm">
    <div class="container-fluid">
      <router-link class="navbar-brand fw-bold" to="/">Travel Planner</router-link>
      <button
        class="navbar-toggler"
        type="button"
        data-bs-toggle="collapse"
        data-bs-target="#navbarNav"
        aria-controls="navbarNav"
        aria-expanded="false"
        aria-label="Toggle navigation"
      >
        <span class="navbar-toggler-icon"></span>
      </button>

      <div class="collapse navbar-collapse" id="navbarNav">
        <ul class="navbar-nav ms-auto gap-3">
          <li class="nav-item">
            <router-link class="nav-link" to="/">Home</router-link>
          </li>
          <li class="nav-item" v-if="!isLoggedIn">
            <router-link class="nav-link" to="/login">Login</router-link>
          </li>
          <li class="nav-item" v-if="!isLoggedIn">
            <router-link class="nav-link" to="/register">Register</router-link>
          </li>
          <li class="nav-item dropdown" v-if="isLoggedIn">
            <a class="nav-link dropdown-toggle d-flex align-items-center" href="#" role="button" data-bs-toggle="dropdown" aria-expanded="false">
              <span class="me-2">👤</span>
              <span class="d-none d-sm-inline">{{ userName }}</span>
            </a>
            <ul class="dropdown-menu dropdown-menu-end">
              <li>
                <router-link class="dropdown-item" to="/user">My Page</router-link>
              </li>
              <li><hr class="dropdown-divider"></li>
              <li>
                <button class="dropdown-item" @click="logout">Logout</button>
              </li>
            </ul>
          </li>
        </ul>
      </div>
    </div>
  </nav>
</template>

<script>
export default {
  name: "Navbar",
  computed: {
    isLoggedIn() {
      const token = localStorage.getItem('token')
      return !!token
    },
    userName() {
      return localStorage.getItem('userName') || 'User'
    }
  },
  methods: {
    logout() {
      localStorage.removeItem('token')
      // keep name/email if you want? We clear for simplicity
      // localStorage.removeItem('userName')
      // localStorage.removeItem('userEmail')
      this.$router.push('/')
    }
  }
};
</script>

<style scoped>
.router-link-active {
  font-weight: 600;
  text-decoration: underline;
  color: #ffc107 !important; /* Amber highlight */
}

.nav-link:hover {
  color: #f8f9fa !important;
  text-decoration: none;
  transition: color 0.2s;
}
</style>

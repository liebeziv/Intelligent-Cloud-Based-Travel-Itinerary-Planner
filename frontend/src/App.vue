<template>
  <div id="app">
    <nav class="navbar navbar-expand-lg navbar-dark bg-dark">
      <div class="container">
        <router-link class="navbar-brand" to="/">
          <i class="fas fa-plane me-2"></i>Travel Planner
        </router-link>

        <div class="navbar-nav ms-auto" v-if="!isLoggedIn">
          <router-link class="nav-link" to="/login" @click="notifyAuthChange">Login</router-link>
          <router-link class="nav-link" to="/register" @click="notifyAuthChange">Register</router-link>
        </div>
        
        <div class="navbar-nav ms-auto align-items-center" v-else>
          <router-link class="nav-link me-2" to="/user">My Trips</router-link>
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
  data() {
    return {
      auth: this.readAuthState()
    }
  },
  computed: {
    isLoggedIn() {
      return !!this.auth.token
    },
    userName() {
      if (this.auth.name) {
        return this.auth.name
      }
      if (this.auth.email) {
        return this.auth.email.split('@')[0]
      }
      return 'User'
    }
  },
  methods: {
    readAuthState() {
      return {
        token: localStorage.getItem('token') || '',
        name: localStorage.getItem('userName') || '',
        email: localStorage.getItem('userEmail') || ''
      }
    },
    notifyAuthChange() {
      window.dispatchEvent(new Event('auth-changed'))
    },
    syncAuthState() {
      this.auth = this.readAuthState()
    },
    logout() {
      localStorage.removeItem('token')
      localStorage.removeItem('userName')
      localStorage.removeItem('userEmail')
      localStorage.removeItem('userId')
      this.syncAuthState()
      this.notifyAuthChange()
      this.$router.push({ name: 'Home' })
    }
  },
  mounted() {
    window.addEventListener('auth-changed', this.syncAuthState)
    window.addEventListener('storage', this.syncAuthState)
  },
  beforeUnmount() {
    window.removeEventListener('auth-changed', this.syncAuthState)
    window.removeEventListener('storage', this.syncAuthState)
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
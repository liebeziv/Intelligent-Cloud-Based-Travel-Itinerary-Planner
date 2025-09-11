<template>
  <div class="container mt-4" style="max-width: 400px;">
    <h2 class="text-center">Login</h2>
    <form @submit.prevent="login">
      <div class="mb-3">
        <label for="email" class="form-label">Email</label>
        <input type="email" id="email" v-model="email" class="form-control" required>
      </div>

      <div class="mb-3">
        <label for="password" class="form-label">Password</label>
        <div class="input-group">
          <input
            :type="showPassword ? 'text' : 'password'"
            id="password"
            v-model="password"
            class="form-control"
            required
          >
          <button
            type="button"
            class="btn btn-outline-secondary"
            @click="togglePassword"
          >
            {{ showPassword ? 'Hide' : 'Show' }}
          </button>
        </div>
      </div>

      <button type="submit" class="btn btn-primary w-100">Login</button>
    </form>
    <p class="mt-3">Don't have an account? <router-link to="/register">Register here</router-link></p>
  </div>
</template>

<script>
import { authAPI } from '../services/api.js'  

export default {
  name: 'Login',
  data() {
    return {
      email: '',
      password: '',
      showPassword: false
    }
  },
  methods: {
    togglePassword() {
      this.showPassword = !this.showPassword
    },

    async login() {
      try {
        const response = await authAPI.login({
          email: this.email,
          password: this.password
        })

        localStorage.setItem('token', response.data.access_token)
        alert('Login successful!')
        this.$router.push('/') 

      } catch (error) {
        console.error(error)
        alert(error.response?.data?.detail || 'Login failed')
      }
    }
  }
}
</script>

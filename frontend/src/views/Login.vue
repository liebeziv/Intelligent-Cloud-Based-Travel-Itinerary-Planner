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
        <input type="password" id="password" v-model="password" class="form-control" required>
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
      password: ''
    }
  },
  methods: {
    async login() {
      try {
        const response = await authAPI.login({
          email: this.email,
          password: this.password
        })

        // store JWT token in localStorage
        localStorage.setItem('token', response.data.access_token)

        alert('Login successful!')
        this.$router.push('/')  // redirect to home page

      } catch (error) {
        console.error(error)
        alert(error.response?.data?.detail || 'Login failed')
      }
    }
  }
}
</script>

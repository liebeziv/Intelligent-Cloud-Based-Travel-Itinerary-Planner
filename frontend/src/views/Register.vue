<template>
  <div class="container mt-4" style="max-width: 400px;">
    <h2 class="text-center">Register</h2>
    <form @submit.prevent="register">
      <div class="mb-3">
        <label for="name" class="form-label">Full Name</label>
        <input type="text" id="name" v-model="name" class="form-control" required>
      </div>
      <div class="mb-3">
        <label for="email" class="form-label">Email</label>
        <input type="email" id="email" v-model="email" class="form-control" required>
      </div>
      <div class="mb-3">
        <label for="password" class="form-label">Password</label>
        <input type="password" id="password" v-model="password" class="form-control" required>
      </div>
      <button type="submit" class="btn btn-primary w-100">Register</button>
    </form>
    <p class="mt-3">Already have an account? <router-link to="/login">Login here</router-link></p>
  </div>
</template>

<script>
export default {
  name: 'Register',
  data() {
    return {
      name: '',
      email: '',
      password: ''
    }
  },
  methods: {
    async register() {
      try {
        // TODO: change the URL backend using AWS server
        const response = await fetch("http://localhost:8000/api/auth/register", {
          method: "POST",
          headers: {
            "Content-Type": "application/json"
          },
          body: JSON.stringify({
            name: this.name,
            email: this.email,
            password: this.password
          })
        });

        if (!response.ok) {
          const err = await response.json();
          throw new Error(err.detail || "Registration failed");
        }

        alert("Registration successful! Please login.");
        this.$router.push("/login");

      } catch (error) {
        alert("Error: " + error.message);
      }
    }
  }
}
</script>

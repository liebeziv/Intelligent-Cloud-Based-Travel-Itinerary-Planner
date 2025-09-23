<template>
  <div class="container mt-4" style="max-width: 400px;">
    <h2 class="text-center">Registration</h2>
    <form @submit.prevent="register">
      <div class="mb-3">
        <label for="name" class="form-label">Name</label>
        <input type="text" id="name" v-model="name" class="form-control" required>
      </div>

      <div class="mb-3">
        <label for="email" class="form-label">Email</label>
        <input type="email" id="email" v-model="email" class="form-control" required>
      </div>

      <!-- Password input with show/hide button -->
      <div class="mb-3">
        <label for="password" class="form-label">Password</label>
        <div class="input-group">
          <input
            :type="showPassword ? 'text' : 'password'"
            id="password"
            v-model="password"
            class="form-control"
            required
          />
          <button
            type="button"
            class="btn btn-outline-secondary"
            @click="togglePassword"
          >
            {{ showPassword ? 'Hide' : 'Show' }}
          </button>
        </div>
      </div>

      <div v-if="password && !isStrongPassword(password)" class="text-danger mb-3">
        <div v-if="password" class="mb-3 text-danger">
          <p>Password must include:</p>
          <ul>
            <li :class="{ 'text-success': password.length >= 8 }">At least 8 characters</li>
            <li :class="{ 'text-success': /[A-Z]/.test(password) }">At least one uppercase letter</li>
            <li :class="{ 'text-success': /[a-z]/.test(password) }">At least one lowercase letter</li>
            <li :class="{ 'text-success': /\d/.test(password) }">At least one number</li>
            <li :class="{ 'text-success': /[^\w\s]/.test(password) }">At least one symbol</li>
          </ul>
        </div>

      </div>

      <button type="submit" class="btn btn-primary w-100" :disabled="!isStrongPassword(password)">
        Register
      </button>
    </form>

    <p class="mt-3">
      Already have an account? <router-link to="/login">Login here</router-link>
    </p>
  </div>
</template>

<script>
export default {
  name: 'Register',
  data() {
    return {
      name: '',
      email: '',
      password: '',
      showPassword: false
    }
  },
  methods: {
    togglePassword() {
      this.showPassword = !this.showPassword;
    },
    isStrongPassword(password) {
      return /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[^\w\s]).{8,}$/.test(password);
    },
    async register() {
      if (!this.isStrongPassword(this.password)) {
        alert("Password does not meet requirement");
        return;
      }

      try {
        const response = await fetch("https://aitravelplan.site/api/auth/register", {
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

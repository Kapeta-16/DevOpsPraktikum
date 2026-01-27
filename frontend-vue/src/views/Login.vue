<template>
  <div class="login-page">
    <div class="login-container">
      <div class="login-header">
        <img :src="logoSvg" alt="Zlatni Čips" class="login-logo" />
        <h2>Prijava</h2>
        <p class="login-subtitle">Dobrodošli natrag!</p>
      </div>
      
      <form @submit.prevent="login" class="login-form">
        <div class="form-group">
          <label for="username">Korisničko ime</label>
          <input 
            id="username"
            v-model="username" 
            type="text"
            placeholder="Unesite korisničko ime" 
            required 
          />
        </div>
        
        <div class="form-group">
          <label for="password">Lozinka</label>
          <input
            id="password"
            v-model="password"
            type="password"
            placeholder="Unesite lozinku"
            required
          />
        </div>
        
        <button type="submit" class="login-btn" :disabled="loading">
          {{ loading ? 'Prijava...' : 'Prijavi se' }}
        </button>
      </form>
      
      <div v-if="error" class="error-message">
        {{ error }}
      </div>
      
      <div class="login-footer">
        <p>Nemate račun? <router-link to="/register" class="register-link">Registrirajte se</router-link></p>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from "vue";
import { useUserStore } from "../stores/user";
import { useRouter } from "vue-router";
import logoSvg from "../assets/logo.svg";

const username = ref("");
const password = ref("");
const error = ref("");
const loading = ref(false);
const userStore = useUserStore();
const router = useRouter();

async function login() {
  error.value = "";
  loading.value = true;
  try {
    const res = await fetch(`${import.meta.env.VITE_API_URL}/login`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        username: username.value,
        password: password.value,
      }),
    });
    const data = await res.json();
    if (!res.ok) throw new Error(data.error || "Pogrešno korisničko ime ili lozinka");
    userStore.login(data.username, data.admin);
    router.push("/");
  } catch (e: any) {
    error.value = e.message;
  } finally {
    loading.value = false;
  }
}
</script>

<style scoped>
.login-page {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: white;
  padding: 20px;
}

.login-container {
  background: white;
  border-radius: 20px;
  box-shadow: 0 10px 40px rgba(16, 73, 17, 0.2);
  padding: 40px;
  width: 100%;
  max-width: 400px;
  border: 2px solid #F9A620;
}

.login-header {
  text-align: center;
  margin-bottom: 30px;
}

.login-logo {
  width: 80px;
  height: 80px;
  margin-bottom: 15px;
}

.login-header h2 {
  margin: 0;
  font-size: 2em;
  color: #104911;
}

.login-subtitle {
  color: #666;
  margin-top: 8px;
  font-size: 1em;
}

.login-form {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.form-group label {
  font-weight: 600;
  color: #104911;
  font-size: 0.95em;
}

.form-group input {
  padding: 14px 16px;
  border: 2px solid #AAB03C;
  border-radius: 10px;
  font-size: 1em;
  transition: border-color 0.2s, box-shadow 0.2s;
  outline: none;
}

.form-group input:focus {
  border-color: #F9A620;
  box-shadow: 0 0 0 3px rgba(249, 166, 32, 0.2);
}

.form-group input::placeholder {
  color: #aaa;
}

.login-btn {
  background: linear-gradient(135deg, #104911 0%, #548C2F 100%);
  color: white;
  border: none;
  padding: 16px;
  border-radius: 10px;
  font-size: 1.1em;
  font-weight: 700;
  cursor: pointer;
  transition: transform 0.2s, box-shadow 0.2s;
  margin-top: 10px;
}

.login-btn:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(16, 73, 17, 0.4);
}

.login-btn:disabled {
  opacity: 0.7;
  cursor: not-allowed;
}

.error-message {
  margin-top: 20px;
  padding: 12px;
  background: #f8d7da;
  color: #721c24;
  border-radius: 10px;
  text-align: center;
  font-size: 0.95em;
}

.login-footer {
  margin-top: 25px;
  text-align: center;
  color: #666;
}

.login-footer p {
  margin: 0;
}

.register-link {
  color: #F9A620;
  font-weight: 600;
  text-decoration: none;
}

.register-link:hover {
  color: #104911;
  text-decoration: underline;
}
</style>

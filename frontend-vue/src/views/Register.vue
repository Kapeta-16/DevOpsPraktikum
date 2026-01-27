<template>
  <div class="register-page">
    <div class="register-container">
      <div class="register-header">
        <img :src="logoSvg" alt="Zlatni Čips" class="register-logo" />
        <h2>Registracija</h2>
        <p class="register-subtitle">Kreirajte novi račun</p>
      </div>
      
      <form @submit.prevent="register" class="register-form">
        <div class="form-group">
          <label for="username">Korisničko ime</label>
          <input 
            id="username"
            v-model="username" 
            type="text"
            placeholder="Unesite korisničko ime" 
            required 
            minlength="3"
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
            minlength="4"
          />
        </div>
        
        <div class="form-group">
          <label for="confirmPassword">Potvrdite lozinku</label>
          <input
            id="confirmPassword"
            v-model="confirmPassword"
            type="password"
            placeholder="Ponovite lozinku"
            required
          />
        </div>
        
        <button type="submit" class="register-btn" :disabled="loading">
          {{ loading ? 'Registracija...' : 'Registriraj se' }}
        </button>
      </form>
      
      <div v-if="error" class="error-message">
        {{ error }}
      </div>
      
      <div v-if="success" class="success-message">
        Registracija uspješna! Preusmjeravanje...
      </div>
      
      <div class="register-footer">
        <p>Već imate račun? <router-link to="/login" class="login-link">Prijavite se</router-link></p>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from "vue";
import { useRouter } from "vue-router";
import logoSvg from "../assets/logo.svg";

const username = ref("");
const password = ref("");
const confirmPassword = ref("");
const error = ref("");
const success = ref(false);
const loading = ref(false);
const router = useRouter();

async function register() {
  error.value = "";
  success.value = false;
  
  // Validate passwords match
  if (password.value !== confirmPassword.value) {
    error.value = "Lozinke se ne podudaraju";
    return;
  }
  
  loading.value = true;
  try {
    const res = await fetch(`${import.meta.env.VITE_API_URL}/signup`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        username: username.value,
        password: password.value,
      }),
    });
    const data = await res.json();
    if (!res.ok) throw new Error(data.error || "Registracija nije uspjela");
    
    success.value = true;
    // Redirect to login after successful registration
    setTimeout(() => {
      router.push("/login");
    }, 1500);
  } catch (e: any) {
    error.value = e.message;
  } finally {
    loading.value = false;
  }
}
</script>

<style scoped>
.register-page {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: white;
  padding: 20px;
}

.register-container {
  background: white;
  border-radius: 20px;
  box-shadow: 0 10px 40px rgba(16, 73, 17, 0.2);
  padding: 40px;
  width: 100%;
  max-width: 400px;
  border: 2px solid #F9A620;
}

.register-header {
  text-align: center;
  margin-bottom: 30px;
}

.register-logo {
  width: 80px;
  height: 80px;
  margin-bottom: 15px;
}

.register-header h2 {
  margin: 0;
  font-size: 2em;
  color: #104911;
}

.register-subtitle {
  color: #666;
  margin-top: 8px;
  font-size: 1em;
}

.register-form {
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

.register-btn {
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

.register-btn:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(16, 73, 17, 0.4);
}

.register-btn:disabled {
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

.success-message {
  margin-top: 20px;
  padding: 12px;
  background: #548C2F;
  color: white;
  border-radius: 10px;
  text-align: center;
  font-size: 0.95em;
}

.register-footer {
  margin-top: 25px;
  text-align: center;
  color: #666;
}

.register-footer p {
  margin: 0;
}

.login-link {
  color: #F9A620;
  font-weight: 600;
  text-decoration: none;
}

.login-link:hover {
  color: #104911;
  text-decoration: underline;
}
</style>

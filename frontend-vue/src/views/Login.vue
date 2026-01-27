<template>
  <div>
    <h2>Login</h2>
    <form @submit.prevent="login">
      <input v-model="username" placeholder="Username" required />
      <input
        v-model="password"
        type="password"
        placeholder="Password"
        required
      />
      <button type="submit">Login</button>
    </form>
    <div v-if="error" style="color: red">Username or password is incorrect</div>
  </div>
</template>

<script setup lang="ts">
import { ref } from "vue";
import { useUserStore } from "../stores/user";
import { useRouter } from "vue-router";

const username = ref("");
const password = ref("");
const error = ref("");
const userStore = useUserStore();
const router = useRouter();

async function login() {
  error.value = "";
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
    if (!res.ok) throw new Error(data.error || "Login failed");
    userStore.login(data.username, data.admin);
    router.push("/");
  } catch (e: any) {
    error.value = e.message;
  }
}
</script>

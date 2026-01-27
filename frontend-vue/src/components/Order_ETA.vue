<template>
  <div>
    <h2>Check Your Order ETA</h2>
    <form @submit.prevent="fetchOrder">
      <input v-model="orderId" placeholder="Order ID" required />
      <button type="submit">Check</button>
    </form>
    <div v-if="error" style="color: red">{{ error }}</div>
    <div v-if="order">
      <h3>Order #{{ orderId }}</h3>
      <div>Status: {{ order.status }}</div>
      <div>Placed at: {{ order.placed_at }}</div>
      <div>ETA: {{ order.eta_delivery }}</div>
      <div>
        Time remaining: <span v-if="etaLeft !== null">{{ etaLeft }}</span
        ><span v-else>Delivered</span>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from "vue";
import { useUserStore } from "../stores/user";

const userStore = useUserStore();
const orderId = ref("");
const error = ref("");
const order = ref<any>(null);

const etaLeft = computed(() => {
  if (!order.value) return null;
  const eta = new Date(order.value.eta_delivery).getTime();
  const now = Date.now();
  if (now > eta) return null;
  const mins = Math.floor((eta - now) / 60000);
  const secs = Math.floor(((eta - now) % 60000) / 1000);
  return `${mins} min ${secs} sec`;
});

async function fetchOrder() {
  error.value = "";
  order.value = null;

  if (!userStore.username) {
    error.value = "Please log in first.";
    return;
  }
  try {
    // Backend endpoint
    const res = await fetch(
      `${import.meta.env.VITE_API_URL}/narudba/${orderId.value}`
    );
    const data = await res.json();
    if (!res.ok) throw new Error(data.error || "Order not found");
    // Security: Only show if the logged-in user owns this order
    if (data.customer_info !== userStore.username)
      throw new Error("Not authorized");
    order.value = data;
  } catch (e: any) {
    error.value = e.message;
  }
}
</script>

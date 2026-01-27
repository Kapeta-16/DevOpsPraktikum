<template>
  <div>
    <h2>My Orders</h2>
    <div v-if="error" style="color: red">{{ error }}</div>
    <ul v-if="orders.length">
      <li v-for="order in orders" :key="order.order_number">
        <b>Order #{{ order.order_number }}</b> — Status: {{ order.status
        }}<br />
        Placed: {{ order.placed_at }} | ETA: {{ order.eta_delivery }}
        <ul>
          <li v-for="item in order.items || []" :key="item.id">
            {{ item.name || item.ime }} x{{ item.quantity || item.kolicina }}
            {{ item.price_euro || item.cijena }} €
          </li>
        </ul>
      </li>
    </ul>
    <div v-else-if="!loading">No orders found.</div>
    <div v-if="loading">Loading...</div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from "vue";
import { useUserStore } from "../stores/user";

const userStore = useUserStore();
const orders = ref<any[]>([]);
const error = ref("");
const loading = ref(true);

async function fetchOrders() {
  error.value = "";
  orders.value = [];
  loading.value = true;
  if (!userStore.username) {
    error.value = "Please log in first.";
    loading.value = false;
    return;
  }
  try {
    // Assumes backend implements /user-orders/<username> that returns all orders for a user
    const res = await fetch(
      `${import.meta.env.VITE_API_URL}/user-orders/${userStore.username}`
    );
    const data = await res.json();
    if (!res.ok) throw new Error(data.error || "Could not fetch orders");
    orders.value = data.orders || data; // flexible if returns array or {orders: [...]}
  } catch (e: any) {
    error.value = e.message;
  } finally {
    loading.value = false;
  }
}

onMounted(fetchOrders);
</script>

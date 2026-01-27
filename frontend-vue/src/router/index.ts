import { createRouter, createWebHistory } from "vue-router";
import Home from "../views/Home.vue";
import Login from "../views/Login.vue";
import Register from "../views/Register.vue";
import UserOrders from "../views/UserOrders.vue";
import Orders from "../views/Orders.vue";

const routes = [
  { path: "/", name: "Home", component: Home },
  { path: "/login", name: "Login", component: Login },
  { path: "/register", name: "Register", component: Register },
  { path: "/orders", name: "UserOrders", component: UserOrders },
  { path: "/admin/orders", name: "AdminOrders", component: Orders },
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

export default router;

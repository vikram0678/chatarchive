import { createRouter, createWebHistory } from "vue-router";
import DashboardView from "../views/DashboardView.vue";
import ConversationDetailView from "../views/ConversationDetailView.vue";

const routes = [
  { path: "/", name: "dashboard", component: DashboardView },
  {
    path: "/conversations/:id",
    name: "conversation-detail",
    component: ConversationDetailView,
    props: true,
  },
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

export default router;
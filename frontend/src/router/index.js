import { createRouter, createWebHistory } from "vue-router";

const routes = [
  {
    path: "/",
    name: "landing",
    component: () => import("../views/LandingView.vue"),
  },
  {
    path: "/districts",
    name: "districts",
    component: () => import("../views/DistrictSelectView.vue"),
  },
  {
    path: "/gu/:gu",
    name: "district",
    component: () => import("../views/DistrictView.vue"),
    props: true,
  },
  {
    path: "/gu/:gu/posts/new",
    name: "post-new",
    component: () => import("../views/PostFormView.vue"),
    props: true,
  },
  {
    path: "/gu/:gu/posts/:id",
    name: "post-detail",
    component: () => import("../views/PostDetailView.vue"),
    props: true,
  },
  {
    path: "/gu/:gu/posts/:id/edit",
    name: "post-edit",
    component: () => import("../views/PostFormView.vue"),
    props: true,
  },
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

export default router;

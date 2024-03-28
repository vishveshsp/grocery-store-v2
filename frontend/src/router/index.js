import Vue from 'vue';
import VueRouter from 'vue-router';
import Home from '../views/Home.vue';
import Signup from '../views/Signup.vue';
import Login from '../views/Login.vue';
import Ping from '../components/Ping.vue';
import Dashboard from '../views/Dashboard.vue';
import ItemTable from '../views/Storefront.vue';
import ModifyTable from '../views/AdminDash.vue';
import OwnerTable from '../views/OwnerDash.vue';

Vue.use(VueRouter);

const routes = [
  {
    path: '/',
    name: 'Home',
    component: Home,
  },
  {
    path: '/ping',
    name: 'Ping',
    component: Ping,
  },
  {
    path: '/signup',
    name: 'Signup',
    component: Signup,
  },
  {
    path: '/login',
    name: 'Login',
    component: Login,
  },
  {
    path: '/owner/dashboard',
    name: 'Dashboard',
    component: Dashboard,
  },
  {
    path: '/user/items',
    name: 'ItemTable',
    component: ItemTable,
  },
  {
    path: '/admin/modifyItems',
    name: 'ModifyTable',
    component: ModifyTable,
  },
  {
    path: '/owner/manage_category',
    name: 'OwnerDash',
    component: OwnerTable,
  },
];

const router = new VueRouter({
  mode: 'history',
  base: process.env.BASE_URL,
  routes,
});

export default router;

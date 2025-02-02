import axios from 'axios';
import router from '../router';
import store from '../store';

axios.interceptors.response.use(undefined, (err) => {
  if (err.response.status === 401) {
    store.commit('logout');
    router.push('/login');
  }
  return err;
});

const axiosPlugin = {
  install(Vue) {
    Vue.prototype.$axios = axios;
    Vue.prototype.$setupAxios = function () {
      this.$axios.defaults.baseURL = 'http://127.0.0.1:8000';
      this.$axios.defaults.headers['Content-Type'] = 'application/json';
    };
  },
};

export default axiosPlugin;

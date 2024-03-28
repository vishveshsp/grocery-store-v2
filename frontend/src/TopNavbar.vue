<template>
  <div>
    <b-navbar variant="light" class="bg-light">
      <b-navbar-nav>
        <b-nav-item to="/" class="nav-link">HOME</b-nav-item>
      </b-navbar-nav>
      <b-navbar-nav class="ms-auto">
        <b-nav-item v-if="!LoginStatus" to="/login" class="nav-link">LOGIN</b-nav-item>
        <b-nav-item v-if="!LoginStatus" to="/signup" class="nav-link">SIGNUP</b-nav-item>
        <b-nav-item v-if="LoginStatus" to="/logout" class="nav-link">LOGOUT</b-nav-item>
      </b-navbar-nav>
    </b-navbar>
  </div>
</template>

<script>

export default {
  name: 'TopNavBar',
  computed: {
    LoginStatus() {
      return this.$store.state.login_status;
    },
  },
};

</script>

<style scoped>

.navbar {
  padding: 10px 10px;
  background-color: #253357 !important;
}
.navbar-nav {
  padding: 0 15px;
}

.nav-link {
  font-weight: bolder;
  color: #fbfafa;
}

</style>

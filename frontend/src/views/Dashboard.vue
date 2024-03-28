<template>
  <DashboardTable v-if="isOwner" />
  <p v-else>Unauthorized access</p>
</template>

<script>
import DashboardTable from '../components/DashboardTable.vue';

export default {
  name: 'Dashboard',
  components: {
    DashboardTable,
  },
  data() {
    return {
      isOwner: false,
    };
  },
  created() {
    const { token } = this.$store.state;
    if (!token) {
      // Redirect to login page or handle unauthorized access
      this.$router.push({ name: 'Login' });
    } else {
      // Check for owner token
      this.$axios.post('/validate_owner_token', { token }).then((response) => {
        if (response.data.is_owner) {
          this.isOwner = true; // Set isOwner to true if the user is an owner
        }
      }).catch((error) => {
        console.error('Error validating owner token:', error);
        // Handle token validation error - Redirect or display an error message
        this.$router.push({ name: 'TokenValidationError' });
      });
    }
  },
};
</script>

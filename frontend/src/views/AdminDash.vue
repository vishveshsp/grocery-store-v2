<template>
  <div class="storefront">
      <ModifyTable v-if="isAdmin" />
      <p v-else>Unauthorized access</p>
  </div>
</template>

<script>
import ModifyTable from '@/components/ModifyTable.vue';

export default {
  name: 'AdminDash',
  components: {
    ModifyTable,
  },
  data() {
    return {
      isAdmin: false,
    };
  },
  created() {
    const { token } = this.$store.state;
    if (!token) {
    // Redirect to login page or handle unauthorized access
      this.$router.push({ name: 'Login' });
    } else {
    // Check for admin token
      this.$axios.post('/validate_manager', { token }).then((response) => {
        if (response.data.is_admin) {
          this.isAdmin = true; // Set isAdmin to true if the user is an admin
        }
      }).catch((error) => {
        console.error('Error validating admin token:', error);
        // Handle token validation error - Redirect or display an error message
        this.$router.push({ name: 'TokenValidationError' });
      });
    }
  },
};
</script>

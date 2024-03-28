<template>
  <div class="container mt-4">
    <h3 class="mb-4">My Store</h3>
    <router-link :to="{ name: 'OwnerDash' }" class="mb-3">
      <button class="btn btn-primary">Go to Manage Categories</button>
    </router-link>

    <div v-if="filteredTracks.length === 0" class="alert alert-info">
      No entries with requests!
    </div>

    <div v-else>
      <table class="table table-striped">
        <thead class="thead-dark">
          <tr>
            <th>Email</th>
            <th>Last Login</th>
            <th>Is Admin</th>
            <th>Request</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="track in filteredTracks" :key="track.email_id">
            <td>{{ track.email_id }}</td>
            <td>{{ track.last_login }}</td>
            <td>{{ track.is_admin }}</td>
            <td>{{ track.request }}</td>
            <td>
              <button @click="approveUser(track.email_id)" class="btn btn-success">Approve</button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script>
export default {
  name: 'OwnerTable',
  data() {
    return {
      tracks: [],
      categories: [],
      message: 'No message',
    };
  },
  computed: {
    filteredTracks() {
      return this.tracks.filter((track) => track.request !== undefined && track.request !== null);
    },
  },
  beforeRouteEnter(to, from, next) {
    const { token } = this.$store.state;
    if (!token) {
      // Redirect to login page or handle unauthorized access
      next({ name: 'Login' });
    } else {
      // Check for owner token
      this.$axios.post('/validate_owner_token', { token }).then((response) => {
        if (response.data.is_owner) {
          // If owner token is valid, proceed to load the component
          next();
        } else {
          // Handle unauthorized access for non-owners
          // Redirect or display an error message
          next({ name: 'UnauthorizedAccess' });
        }
      }).catch((error) => {
        console.error('Error validating owner token:', error);
        // Handle token validation error - Redirect or display an error message
        next({ name: 'TokenValidationError' });
      });
    }
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
          // If owner token is valid, load data
          this.loadData();
        } else {
          // Handle unauthorized access for non-owners
          // Redirect or display an error message
          this.message = 'Unauthorized access';
        }
      }).catch((error) => {
        console.error('Error validating owner token:', error);
        // Handle token validation error - Redirect or display an error message
        this.message = 'Token validation error';
      });
    }
  },
  methods: {
    loadData() {
      this.$axios.get('/get_credentials').then((res) => {
        if (res.data) {
          this.tracks = res.data;
        }
      });
      // Fetch category requests
      this.$axios.get('/get_category_requests').then((res) => {
        if (res.data) {
          this.categories = res.data;
        }
      });
    },
    approveUser(email) {
      this.$axios.post('/approve_user', { email }).then((res) => {
        // Update the tracks or re-fetch the data to reflect the change in isAdmin
        this.loadData();
      }).catch((error) => {
        console.error('Error approving user:', error);
      });
    },
    approveCategory(categoryId) {
      // Method to approve category requests
      this.$axios.post('/approve_category', { categoryId }).then((res) => {
        // Update the categories or re-fetch the data to reflect the change in category requests
        this.loadData();
      }).catch((error) => {
        console.error('Error approving category:', error);
      });
    },
    declineCategory(categoryId) {
      // Method to decline category requests
      this.$axios.post('/decline_category', { categoryId }).then((res) => {
        // Update the categories or re-fetch the data to reflect the change in category requests
        this.loadData();
      }).catch((error) => {
        console.error('Error declining category:', error);
      });
    },
  },
};

</script>

<style scoped>
/* Add your styling here */
</style>

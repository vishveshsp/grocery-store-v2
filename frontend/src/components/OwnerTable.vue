<template>
  <div class="container mt-4">
    <div>
      <h3>Requests Approval</h3>

      <div v-if="filteredRequests.length === 0" class="alert alert-info">
        No requests to display!
      </div>

      <div v-else>
        <table class="table table-striped">
          <thead>
            <tr>
              <th>Category Name</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="request in filteredRequests" :key="request.id">
              <td>{{ request.name }}</td>
              <td>
                <button @click="approveRequest(request.name)" class="btn btn-success">Approve</button>
                <button @click="declineRequest(request.name)" class="btn btn-danger">Decline</button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <div>
        <h4>Delete Category</h4>
        <select class="form-control" v-model="selectedCategory">
          <option v-for="category in categories" :key="category.id" :value="category.id">
            {{ category.name }}
          </option>
        </select>
        <button @click="deleteCategory" class="btn btn-primary mt-2">Delete Category</button>
      </div>
    </div>
  </div>
</template>
<script>
export default {
  name: 'RequestsApproval',
  data() {
    return {
      requests: [], // Holds requests data fetched from the backend
      categories: [], // Holds categories data fetched from the backend
      selectedCategory: '',
    };
  },
  computed: {
    filteredRequests() {
      // Filter requests based on certain criteria (if needed)
      return this.requests;
    },
  },
  created() {
    // Fetch requests data from the endpoint on component creation
    this.fetchRequests();
    this.fetchCategories();
  },
  methods: {
    fetchRequests() {
      // Make an API call to fetch requests from the "/approvals" endpoint
      this.$axios.get('/approvals')
        .then((response) => {
          this.requests = response.data;
        })
        .catch((error) => {
          console.error('Error fetching requests', error);
        });
    },
    fetchCategories() {
      // Make an API call to fetch categories from the "/item/categories" endpoint
      this.$axios.get('/item/categories')
        .then((response) => {
          this.categories = response.data;
        })
        .catch((error) => {
          console.error('Error fetching categories', error);
        });
    },
    approveRequest(requestId) {
      // Make an API call to approve the specific request by its ID
      this.$axios.post('/approve_request', { requestId })
        .then((response) => {
          console.log('Request approved successfully:', response.data);
          // Refresh the list of requests after approval
          this.fetchRequests();
        })
        .catch((error) => {
          console.error('Error approving request:', error);
        });
    },
    declineRequest(requestId) {
      // Make an API call to decline the specific request by its ID
      this.$axios.post('/decline_request', { requestId })
        .then((response) => {
          console.log('Request declined successfully:', response.data);
          // Refresh the list of requests after decline
          this.fetchRequests();
        })
        .catch((error) => {
          console.error('Error declining request:', error);
        });
    },
    deleteCategory() {
      if (this.selectedCategory) {
        const payload = { categoryId: this.selectedCategory };

        this.$axios.delete('/owner/delete_category', { data: payload })
          .then((response) => {
            console.log('Category deleted successfully:', response.data);
            // Fetch categories again to update the list after deletion
            this.fetchCategories();
          })
          .catch((error) => {
            console.error('Error deleting category:', error);
          });
      } else {
        console.error('Please select a category to delete.');
      }
    },
  },
};
</script>

  <style scoped>
  /* Add your styling here */
  </style>

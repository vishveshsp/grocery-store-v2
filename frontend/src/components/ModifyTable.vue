<template>
  <div class="container mt-4">
    <div class="item-table">
      <div class="form-group">
        <label for="category">Select Category:</label>
        <select class="form-control" v-model="selectedCategory" @change="filterItems">
          <option value="">All</option>
          <option v-for="category in categories" :key="category.id" :value="category.id">
            {{ category.name }}
          </option>
        </select>
      </div>

      <div class="mt-3">
        <button class="btn btn-primary" @click="openCreateDialog">Create Item</button>
        <button class="btn btn-secondary ml-2" @click="downloadCSV">Download CSV</button>
      </div>

      <!-- Item Table -->
      <b-table :items="filteredItems" :fields="fields" class="mt-3">
        <template v-slot:cell(actions)="data">
          <div>
            <button class="btn btn-info" @click="editItem(data.item)">Edit</button>
            <button class="btn btn-danger ml-2" @click="deleteItem(data.item)">Delete</button>
          </div>
        </template>
      </b-table>

      <!-- Edit Modal -->
      <b-modal v-model="isModalOpen" title="Edit Product" @ok="submitChanges">
        <form @submit.prevent="submitChanges">
          <div class="form-group">
            <label>Name</label>
            <input class="form-control" v-model="editedItem.name" />
          </div>
          <div class="form-group">
            <label>Price</label>
            <input class="form-control" v-model="editedItem.price" type="number" />
          </div>
          <div class="form-group">
            <label>Stock Left</label>
            <input class="form-control" v-model="editedItem.stock_left" type="number" />
          </div>
          <div class="form-group">
            <label>Expiration Date</label>
            <input class="form-control" v-model="editedItem.expiration_date" type="date" />
          </div>
          <div class="form-group">
            <label>Category</label>
            <select class="form-control" v-model="editedItem.category_id">
              <option v-for="category in categories" :key="category.id" :value="category.id">
                {{ category.name }}
              </option>
            </select>
          </div>
          <button type="submit" class="btn btn-primary">Submit</button>
        </form>
      </b-modal>

      <!-- Create Category Section -->
      <div class="mt-3">
        <button class="btn btn-success" @click="toggleNewCategory">Create Category</button>
        <form v-if="showNewCategory" @submit.prevent="createCategory" class="mt-3">
          <div class="form-group">
            <label for="newCategoryName">New Category Name:</label>
            <input class="form-control" type="text" id="newCategoryName" v-model="newCategoryName" required>
          </div>
          <button type="submit" class="btn btn-primary">Request</button>
        </form>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'ModifyTable',
  data() {
    return {
      items: [],
      fields: [
        { key: 'name', label: 'Name' },
        { key: 'price', label: 'Price' },
        { key: 'stock_left', label: 'Stock Left' },
        { key: 'image_url', label: '' },
        { key: 'actions', label: 'Actions' },
      ],
      filteredItems: [],
      categories: [], // Holds category data fetched from the backend
      selectedCategory: '',
      cart: [], // Holds cart items
      editedItem: {}, // Edited item data
      isModalOpen: false, // Modal visibility flag
      newItem: {
        name: '',
        price: 0,
        stock_left: 0,
        category_id: '', // Assuming category ID is a string
      },
      showNewCategory: false,
      newCategoryName: '',
    };
  },
  created() {
    this.$axios.defaults.headers.common['x-access-token'] = this.$store.state.token;
    // this.loadData();
    this.fetchItems();
    this.fetchCategories();
  },
  methods: {
    fetchCategories() {
      // Make an API call to fetch categories
      this.$axios.get('/item/categories')
        .then((response) => {
          this.categories = response.data;
        })
        .catch((error) => {
          console.error('Error fetching categories', error);
        });
    },
    toggleNewCategory() {
      this.showNewCategory = !this.showNewCategory;
    },
    createCategory() {
      // Assuming you have a backend route /createcategory that accepts POST requests
      const categoryName = this.newCategoryName.trim();

      if (categoryName) {
        this.$axios.post('/admin/create_category', { name: categoryName })
          .then((response) => {
            console.log('Category created successfully:', response.data);
            // Reset input and hide the form after creating the category
            this.newCategoryName = '';

            // Fetch categories again to update the list with the new category
            this.fetchCategories();
          })
          .catch((error) => {
            console.error('Error creating category:', error);
          });
      } else {
        // Handle empty category name case if required
        console.error('Category name cannot be empty.');
      }
    },
    downloadCSV() {
      // Function to generate CSV content
      const createCSV = () => {
        const header = `${Object.keys(this.filteredItems[0]).join(',')}\n`;

        const rows = this.filteredItems.map((item) => Object.values(item).map((value) => (typeof value === 'string' ? `"${value}"` : value)).join(','));

        return header + rows.join('\n');
      };

      // Create a Blob object from the CSV content
      const csvContent = createCSV();
      const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });

      // Create a temporary URL to trigger the download
      const link = document.createElement('a');
      link.href = window.URL.createObjectURL(blob);
      link.setAttribute('download', 'items.csv');
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
    },
    openCreateDialog() {
      this.isModalOpen = true; // Open the modal for creating a new item
      this.editedItem = { ...this.newItem }; // Populate modal data with empty new item
    },
    editItem(item) {
      // Copy item data to the editedItem object
      this.editedItem = { ...item };
      this.isModalOpen = true; // Open the modal for editing
    },
    deleteItem(item) {
      const itemId = item.id; // Assuming item has an 'id' field
      const payload = { itemId };

      this.$axios.delete('/admin/deleteitem', { data: payload })
        .then((response) => {
          this.fetchItems(); // Updates the list.
        })
        .catch((error) => {

        });
    },
    submitChanges() {
      const itemId = this.editedItem.id;
      const payload = {
        itemId,
        editedItemData: this.editedItem,
      };
      this.$axios.post('/admin/updateitems', payload)
        .then((response) => {
          console.log('Item updated successfully', response.data);
          // Perform any necessary operations after successful update
          this.isModalOpen = false; // Close the modal after the operation is completed
          // Reset the editedItem object if needed
          this.editedItem = {};
          this.fetchItems();
        })
        .catch((error) => {
          console.error('Error updating item', error);
        });
    },
    fetchItems() {
      // Make an API call to fetch items
      this.$axios.get('/admin/modify')
        .then((response) => {
          this.items = response.data.map((item) => ({
            ...item,
            stock_left: item.stock_left === 0 ? 'Out of Stock' : item.stock_left,
          }));
          this.filteredItems = [...this.items]; // Set initial items to display
        })
        .catch((error) => {
          console.error('Error fetching items', error);
        });
    },
    filterItems() {
      if (this.selectedCategory === '') {
        this.filteredItems = [...this.items];
      } else {
        this.filteredItems = this.items.filter((item) => item.category_id === parseInt(this.selectedCategory, 10));
      }
    },
    updateStock(item, change) {
      const itemIndex = this.items.findIndex((i) => i.id === item.id);
      if (itemIndex !== -1) {
        this.$set(this.items[itemIndex], 'stock_left', this.items[itemIndex].stock_left + change);
      }
    },

  },
};
</script>

<style>
/* Styles for cart-preview and other elements */
</style>

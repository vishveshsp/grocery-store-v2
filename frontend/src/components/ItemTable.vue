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
      <div class="form-group">
        <label for="search">Search:</label>
        <input type="text" class="form-control" v-model="searchQuery" @input="searchItems" placeholder="Search items">
      </div>

      <b-table :items="filteredItems" :fields="fields" class="mt-3">
        <template v-slot:cell(actions)="data">
          <div>
            <button @click="addToCart(data.item)" class="btn btn-success mr-2">Add to Cart</button>
            <button @click="removeFromCart(data.item)" class="btn btn-danger">Remove from Cart</button>
          </div>
        </template>
        <template v-slot:cell(expiration_date)="data">
          <span v-if="data.item.expiration_date">{{ data.item.expiration_date }}</span>
          <span v-else>N/A</span>
        </template>
      </b-table>

      <div class="cart-preview mt-4">
        <h3>Cart</h3>
        <ul class="list-group">
          <li class="list-group-item" v-for="cartItem in cart" :key="cartItem.id">
            {{ cartItem.name }} - Quantity: {{ cartItem.quantity }} - Price: {{ calculateItemTotal(cartItem) }}
          </li>
        </ul>
        <div>Total Cart Value: {{ calculateTotalCartValue() }}</div>
        <button @click="commitCart" class="btn btn-primary mt-3">Submit Cart</button>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'ItemTable',
  data() {
    return {
      items: [],
      fields: [
        { key: 'name', label: 'Name' },
        { key: 'price', label: 'Price' },
        { key: 'stock_left', label: 'Stock Left' },
        { key: 'image_url', label: '' },
        { key: 'expiration_date', label: 'Expiration Date' },
        { key: 'actions', label: 'Actions' }, // Added Actions column
      ],
      filteredItems: [],
      categories: [], // Holds category data fetched from the backend
      selectedCategory: '',
      cart: [], // Holds cart items
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
    searchItems() {
      if (this.searchQuery.trim() === '') {
        this.filteredItems = [...this.items]; // Reset to display all items if search query is empty
      } else {
        const searchTerm = this.searchQuery.trim().toLowerCase();
        this.filteredItems = this.items.filter(
          (item) => item.name.toLowerCase().includes(searchTerm),
        );
      }
    },
    fetchItems() {
      // Make an API call to fetch items
      this.$axios.get('/user/items')
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

    addToCart(item) {
      const existingCartItem = this.cart.find((cartItem) => cartItem.id === item.id);
      if (existingCartItem) {
        if (existingCartItem.quantity < item.stock_left) {
          existingCartItem.quantity += 1;
          this.updateStock(item, -1); // Decrease stock_left by 1 when adding to cart
        } else {
          this.$toasted.show('Maximum stock reached for this item', { type: 'error' });
        }
      } else if (item.stock_left > 0) {
        this.cart.push({ ...item, quantity: 1 });
        this.updateStock(item, -1);
      } else {
        this.$toasted.show('Not enough product available', { type: 'error' });
      }
    },
    removeFromCart(item) {
      const existingCartItemIndex = this.cart.findIndex((cartItem) => cartItem.id === item.id);
      if (existingCartItemIndex !== -1) {
        if (this.cart[existingCartItemIndex].quantity > 1) {
          this.cart[existingCartItemIndex].quantity -= 1;
          this.updateStock(item, 1); // Adjust stock_left when removing from cart
        } else {
          this.cart.splice(existingCartItemIndex, 1);
          this.updateStock(item, 1); // Adjust stock_left when removing from cart
        }
      }
    },
    updateStock(item, change) {
      const itemIndex = this.items.findIndex((i) => i.id === item.id);
      if (itemIndex !== -1) {
        this.$set(this.items[itemIndex], 'stock_left', this.items[itemIndex].stock_left + change);
      }
    },

    adjustQuantity(item, action) {
      const existingCartItem = this.cart.find((cartItem) => cartItem.id === item.id);
      if (existingCartItem) {
        switch (action) {
          case 'increment':
            if (existingCartItem.quantity < item.stock_left) {
              existingCartItem.quantity += 1;
              item.stock_left -= 1; // Decrease stock_left when adjusting quantity
            } else {
              console.warn('Maximum stock reached for this item');
            }
            break;
          case 'decrement':
            if (existingCartItem.quantity > 1) {
              existingCartItem.quantity -= 1;
              item.stock_left += 1; // Increase stock_left when adjusting quantity
            }
            break;
          case 'input':
          // Handle manual input changes (if needed)
            break;
          default:
            break;
        }
      }
    },
    calculateItemTotal(item) {
      return item.price * item.quantity;
    },
    calculateTotalCartValue() {
      return this.cart.reduce((total, cartItem) => total + this.calculateItemTotal(cartItem), 0);
    },
    commitCart() {
      const { userId } = this.$store.state; // Assuming you have the user ID stored in Vuex state
      const order = {
        userId,
        cart: this.cart,
      };

      this.$axios.post('/user/commit_cart', order) // Replace with your Flask backend URL
        .then((response) => {
          console.log('Cart submitted successfully', response.data);
          console.log('Data sent to server:', order); // Log the data sent to the server
          this.cart = []; // Clear the cart after submitting
          this.updateItemStock();
          this.fetchItems();
        })
        .catch((error) => {
          console.error('Error submitting cart', error);
        });
    },
    updateItemStock() {
      this.$axios.get('/user/items') // Fetch updated items from backend
        .then((response) => {
          this.items = response.data.map((item) => ({
            ...item,
            stock_left: item.stock_left === 0 ? 'Out of Stock' : item.stock_left,
            expiration_date: item.expiration_date,
          }));
        })
        .catch((error) => {
          console.error('Error updating item stock', error);
        });
    },
  },
};
</script>

<style>
/* Styles for cart-preview and other elements */
</style>

<template>
    <div class="storefront">
        <ItemTable/>
    </div>
</template>

<script>
import ItemTable from '@/components/ItemTable.vue';

export default {
  name: 'Storefront',
  components: {
    ItemTable,
  },
};
</script>

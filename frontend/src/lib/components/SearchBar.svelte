<script>
  import { createEventDispatcher } from 'svelte';
  import { debounce } from '$lib/utils.js';

  const dispatch = createEventDispatcher();
  
  let searchValue = '';

  // Debounced search to avoid excessive API calls
  const debouncedSearch = debounce((query) => {
    dispatch('search', { query });
  }, 500);

  $: if (searchValue !== undefined) {
    debouncedSearch(searchValue);
  }

  function clearSearch() {
    searchValue = '';
  }
</script>

<div class="relative flex-1 max-w-md">
  <div class="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
    <svg class="h-5 w-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
    </svg>
  </div>
  
  <input
    type="text"
    bind:value={searchValue}
    placeholder="Search files and folders..."
    class="block w-full pl-10 pr-10 py-2 border border-gray-300 rounded-md leading-5 bg-white placeholder-gray-500 focus:outline-none focus:placeholder-gray-400 focus:ring-1 focus:ring-blue-500 focus:border-blue-500"
  />
  
  {#if searchValue}
    <div class="absolute inset-y-0 right-0 pr-3 flex items-center">
      <button
        on:click={clearSearch}
        class="text-gray-400 hover:text-gray-600"
        title="Clear search"
      >
        <svg class="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
        </svg>
      </button>
    </div>
  {/if}
</div>
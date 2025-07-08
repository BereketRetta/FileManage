<script>
  import { createEventDispatcher } from 'svelte';
  
  export let breadcrumb = [];
  const dispatch = createEventDispatcher();

  function navigateToFolder(folderId) {
    dispatch('navigate', { folderId });
  }
</script>

<nav class="flex mb-4" aria-label="Breadcrumb">
  <ol class="inline-flex items-center space-x-1 md:space-x-3">
    {#each breadcrumb as item, index}
      <li class="inline-flex items-center">
        {#if index > 0}
          <svg class="w-6 h-6 text-gray-400" fill="currentColor" viewBox="0 0 20 20" xmlns="http://www.w3.org/2000/svg">
            <path fill-rule="evenodd" d="M7.293 14.707a1 1 0 010-1.414L10.586 10 7.293 6.707a1 1 0 011.414-1.414l4 4a1 1 0 010 1.414l-4 4a1 1 0 01-1.414 0z" clip-rule="evenodd"></path>
          </svg>
        {/if}
        
        <button
          on:click={() => navigateToFolder(item.folder_id)}
          class="inline-flex items-center text-sm font-medium text-gray-700 hover:text-blue-600 {index === breadcrumb.length - 1 ? 'text-blue-600 cursor-default' : 'hover:underline'}"
          disabled={index === breadcrumb.length - 1}
        >
          {#if index === 0}
            <svg class="w-4 h-4 mr-2" fill="currentColor" viewBox="0 0 20 20" xmlns="http://www.w3.org/2000/svg">
              <path d="M10.707 2.293a1 1 0 00-1.414 0l-7 7a1 1 0 001.414 1.414L4 10.414V17a1 1 0 001 1h2a1 1 0 001-1v-2a1 1 0 011-1h2a1 1 0 011 1v2a1 1 0 001 1h2a1 1 0 001-1v-6.586l.293.293a1 1 0 001.414-1.414l-7-7z"></path>
            </svg>
          {:else}
            <svg class="w-4 h-4 mr-2" fill="currentColor" viewBox="0 0 20 20" xmlns="http://www.w3.org/2000/svg">
              <path d="M2 6a2 2 0 012-2h5l2 2h5a2 2 0 012 2v6a2 2 0 01-2 2H4a2 2 0 01-2-2V6z"></path>
            </svg>
          {/if}
          {item.name}
        </button>
      </li>
    {/each}
  </ol>
</nav>
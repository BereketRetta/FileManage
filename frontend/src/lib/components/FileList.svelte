<script>
  import { createEventDispatcher } from 'svelte';
  import FileItem from './FileItem.svelte';
  import { formatFileSize, getFileIcon } from '$lib/utils.js';

  export let items = [];
  
  const dispatch = createEventDispatcher();

  let sortBy = 'name';
  let sortOrder = 'asc';

  function handleFileDeleted(event) {
    dispatch('fileDeleted', event.detail);
  }

  function handleFileUpdated(event) {
    dispatch('fileUpdated', event.detail);
  }

  function handleFolderOpen(event) {
    dispatch('folderOpen', event.detail);
  }

  function handleSort(field) {
    if (sortBy === field) {
      sortOrder = sortOrder === 'asc' ? 'desc' : 'asc';
    } else {
      sortBy = field;
      sortOrder = 'asc';
    }
    dispatch('sort', { sortBy, sortOrder });
  }

  function getSortIcon(field) {
    if (sortBy !== field) return '';
    return sortOrder === 'asc' ? '↑' : '↓';
  }

  // Separate folders and files
  $: folders = items.filter(item => item.item_type === 'folder');
  $: files = items.filter(item => item.item_type === 'file');
</script>

<div class="bg-white rounded-lg shadow-sm border border-gray-200">
  <div class="px-6 py-4 border-b border-gray-200">
    <div class="flex justify-between items-center">
      <h2 class="text-lg font-semibold text-gray-900">
        Items ({items.length})
      </h2>
      
      <!-- Sort Controls -->
      <div class="flex space-x-2 text-sm">
        <button
          on:click={() => handleSort('name')}
          class="px-3 py-1 rounded hover:bg-gray-100 {sortBy === 'name' ? 'bg-gray-100 font-medium' : ''}"
        >
          Name {getSortIcon('name')}
        </button>
        <button
          on:click={() => handleSort('upload_date')}
          class="px-3 py-1 rounded hover:bg-gray-100 {sortBy === 'upload_date' || sortBy === 'created_date' ? 'bg-gray-100 font-medium' : ''}"
        >
          Date {getSortIcon('upload_date')}
        </button>
        <button
          on:click={() => handleSort('size')}
          class="px-3 py-1 rounded hover:bg-gray-100 {sortBy === 'size' ? 'bg-gray-100 font-medium' : ''}"
        >
          Size {getSortIcon('size')}
        </button>
      </div>
    </div>
  </div>

  {#if items.length === 0}
    <div class="p-12 text-center">
      <svg class="mx-auto h-12 w-12 text-gray-400 mb-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 21h10a2 2 0 002-2V9.414a1 1 0 00-.293-.707l-5.414-5.414A1 1 0 0012.586 3H7a2 2 0 00-2 2v14a2 2 0 002 2z" />
      </svg>
      <p class="text-gray-500 text-lg mb-2">No items here yet</p>
      <p class="text-gray-400 text-sm">Upload files or create folders to get started</p>
    </div>
  {:else}
    <div class="divide-y divide-gray-200">
      <!-- Display folders first -->
      {#each folders as folder (folder.id)}
        <FileItem 
          item={folder}
          {formatFileSize}
          {getFileIcon}
          on:fileDeleted={handleFileDeleted}
          on:fileUpdated={handleFileUpdated}
          on:folderOpen={handleFolderOpen}
        />
      {/each}
      
      <!-- Then files -->
      {#each files as file (file.id)}
        <FileItem 
          item={file}
          {formatFileSize}
          {getFileIcon}
          on:fileDeleted={handleFileDeleted}
          on:fileUpdated={handleFileUpdated}
          on:folderOpen={handleFolderOpen}
        />
      {/each}
    </div>
  {/if}
</div>
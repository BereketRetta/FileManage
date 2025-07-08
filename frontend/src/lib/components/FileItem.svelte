<script>
  import { createEventDispatcher } from 'svelte';
  import { api } from '$lib/api.js';
  import { formatDate } from '$lib/utils.js';

  export let item;
  export let formatFileSize;
  export let getFileIcon;

  const dispatch = createEventDispatcher();

  let editing = false;
  let editedName = item.name;
  let showDeleteModal = false;
  let deleting = false;
  let updating = false;

  $: isFolder = item.item_type === 'folder';
  $: isFile = item.item_type === 'file';

  function startEdit() {
    editing = true;
    editedName = item.name;
  }

  function cancelEdit() {
    editing = false;
    editedName = item.name;
  }

  async function saveEdit() {
    if (editedName.trim() === '' || editedName === item.name) {
      cancelEdit();
      return;
    }

    updating = true;
    try {
      if (isFolder) {
        await api.updateFolder(item.folder_id, { name: editedName.trim() });
      } else {
        await api.updateFile(item.file_id, { name: editedName.trim() });
      }
      
      item.name = editedName.trim();
      editing = false;
      dispatch('fileUpdated', { fileId: item.file_id || item.folder_id });
    } catch (error) {
      console.error('Error updating item:', error);
      alert('Failed to update item name: ' + error.message);
      cancelEdit();
    } finally {
      updating = false;
    }
  }

  function handleKeydown(event) {
    if (event.key === 'Enter') {
      saveEdit();
    } else if (event.key === 'Escape') {
      cancelEdit();
    }
  }

  function showDeleteConfirm() {
    showDeleteModal = true;
  }

  function hideDeleteModal() {
    showDeleteModal = false;
  }

  async function deleteItem() {
    deleting = true;
    try {
      if (isFolder) {
        await api.deleteFolder(item.folder_id);
      } else {
        await api.deleteFile(item.file_id);
      }
      
      dispatch('fileDeleted', { fileId: item.file_id || item.folder_id });
      hideDeleteModal();
    } catch (error) {
      console.error('Error deleting item:', error);
      alert('Failed to delete item: ' + error.message);
    } finally {
      deleting = false;
    }
  }

  async function downloadFile() {
    if (isFile) {
      try {
        await api.downloadFile(item.file_id, item.name);
      } catch (error) {
        console.error('Error downloading file:', error);
        alert('Failed to download file: ' + error.message);
      }
    }
  }

  function openFolder() {
    if (isFolder) {
      dispatch('folderOpen', { folderId: item.folder_id });
    }
  }

  function getItemIcon() {
    if (isFolder) {
      return '📁';
    }
    return getFileIcon(item.content_type);
  }

  function getItemSize() {
    if (isFolder) {
      return '—';
    }
    return formatFileSize(item.size);
  }

  function getItemDate() {
    const date = isFolder ? item.created_date : item.upload_date;
    return formatDate(date);
  }
</script>

<div class="p-4 hover:bg-gray-50 transition-colors duration-150">
  <div class="flex items-center justify-between">
    <div class="flex items-center space-x-3 flex-1 min-w-0">
      <button
        class="text-2xl flex-shrink-0 {isFolder ? 'hover:scale-110 transition-transform cursor-pointer' : ''}"
        on:click={isFolder ? openFolder : undefined}
        title={isFolder ? 'Open folder' : ''}
      >
        {getItemIcon()}
      </button>
      
      <div class="flex-1 min-w-0">
        {#if editing}
          <div class="flex items-center space-x-2">
            <input
              type="text"
              bind:value={editedName}
              on:keydown={handleKeydown}
              on:blur={saveEdit}
              class="block w-full px-3 py-1 text-sm border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              disabled={updating}
            />
            {#if updating}
              <div class="animate-spin rounded-full h-4 w-4 border-b-2 border-blue-600"></div>
            {/if}
          </div>
        {:else}
          <button
            class="text-left w-full"
            on:click={isFolder ? openFolder : undefined}
          >
            <h3 class="text-sm font-medium text-gray-900 truncate {isFolder ? 'hover:text-blue-600' : ''}">{item.name}</h3>
          </button>
        {/if}
        
        <div class="flex items-center space-x-4 text-xs text-gray-500 mt-1">
          <span>{getItemSize()}</span>
          <span>{getItemDate()}</span>
          {#if isFile}
            <span class="hidden sm:inline">{item.content_type}</span>
          {/if}
        </div>
      </div>
    </div>

    <div class="flex items-center space-x-1 ml-4">
      {#if !editing}
        {#if isFile}
          <button
            on:click={downloadFile}
            class="p-2 text-gray-400 hover:text-blue-600 hover:bg-blue-50 rounded-md transition-colors duration-150"
            title="Download"
          >
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
            </svg>
          </button>
        {/if}

        <button
          on:click={startEdit}
          class="p-2 text-gray-400 hover:text-yellow-600 hover:bg-yellow-50 rounded-md transition-colors duration-150"
          title="Edit name"
        >
          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
          </svg>
        </button>

        <button
          on:click={showDeleteConfirm}
          class="p-2 text-gray-400 hover:text-red-600 hover:bg-red-50 rounded-md transition-colors duration-150"
          title="Delete"
        >
          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
          </svg>
        </button>
      {:else}
        <button
          on:click={saveEdit}
          class="p-2 text-gray-400 hover:text-green-600 hover:bg-green-50 rounded-md transition-colors duration-150"
          title="Save"
          disabled={updating}
        >
          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
          </svg>
        </button>

        <button
          on:click={cancelEdit}
          class="p-2 text-gray-400 hover:text-red-600 hover:bg-red-50 rounded-md transition-colors duration-150"
          title="Cancel"
          disabled={updating}
        >
          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
          </svg>
        </button>
      {/if}
    </div>
  </div>
</div>

<!-- Delete Confirmation Modal -->
{#if showDeleteModal}
  <div class="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50">
    <div class="relative top-20 mx-auto p-5 border w-96 shadow-lg rounded-md bg-white">
      <div class="mt-3 text-center">
        <div class="mx-auto flex items-center justify-center h-12 w-12 rounded-full bg-red-100">
          <svg class="h-6 w-6 text-red-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L3.732 16.5c-.77.833.192 2.5 1.732 2.5z" />
          </svg>
        </div>
        <h3 class="text-lg leading-6 font-medium text-gray-900 mt-2">Delete {isFolder ? 'Folder' : 'File'}</h3>
        <div class="mt-2 px-7 py-3">
          <p class="text-sm text-gray-500">
            Are you sure you want to delete "<span class="font-medium">{item.name}</span>"? 
            {#if isFolder}
              This folder must be empty to delete it.
            {/if}
            This action cannot be undone.
          </p>
        </div>
        <div class="items-center px-4 py-3">
          <div class="flex space-x-3">
            <button
              on:click={hideDeleteModal}
              class="px-4 py-2 bg-gray-500 text-white text-base font-medium rounded-md w-full shadow-sm hover:bg-gray-600 focus:outline-none focus:ring-2 focus:ring-gray-300"
              disabled={deleting}
            >
              Cancel
            </button>
            <button
              on:click={deleteItem}
              class="px-4 py-2 bg-red-600 text-white text-base font-medium rounded-md w-full shadow-sm hover:bg-red-700 focus:outline-none focus:ring-2 focus:ring-red-300 disabled:opacity-50"
              disabled={deleting}
            >
              {#if deleting}
                <div class="flex items-center justify-center">
                  <div class="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                  Deleting...
                </div>
              {:else}
                Delete
              {/if}
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
{/if}
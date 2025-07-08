<script>
  import { createEventDispatcher } from 'svelte';
  import { api } from '$lib/api.js';

  export let show = false;
  export let currentFolderId = null;

  const dispatch = createEventDispatcher();

  let folderName = '';
  let creating = false;
  let error = '';

  function closeModal() {
    show = false;
    folderName = '';
    error = '';
  }

  async function createFolder() {
    if (!folderName.trim()) {
      error = 'Folder name is required';
      return;
    }

    creating = true;
    error = '';

    try {
      await api.createFolder({
        name: folderName.trim(),
        parent_folder_id: currentFolderId
      });

      dispatch('folderCreated');
      closeModal();
    } catch (err) {
      error = err.message;
    } finally {
      creating = false;
    }
  }

  function handleKeydown(event) {
    if (event.key === 'Enter') {
      createFolder();
    } else if (event.key === 'Escape') {
      closeModal();
    }
  }
</script>

{#if show}
  <div class="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50">
    <div class="relative top-20 mx-auto p-5 border w-96 shadow-lg rounded-md bg-white">
      <div class="mt-3">
        <h3 class="text-lg leading-6 font-medium text-gray-900 mb-4">Create New Folder</h3>
        
        <div class="mb-4">
          <label for="folderName" class="block text-sm font-medium text-gray-700 mb-2">
            Folder Name
          </label>
          <input
            id="folderName"
            type="text"
            bind:value={folderName}
            on:keydown={handleKeydown}
            placeholder="Enter folder name"
            class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            disabled={creating}
          />
        </div>

        {#if error}
          <div class="mb-4 p-3 bg-red-50 border border-red-200 rounded-md">
            <p class="text-sm text-red-700">{error}</p>
          </div>
        {/if}

        <div class="flex justify-end space-x-3">
          <button
            on:click={closeModal}
            class="px-4 py-2 bg-gray-500 text-white text-sm font-medium rounded-md hover:bg-gray-600 focus:outline-none focus:ring-2 focus:ring-gray-300"
            disabled={creating}
          >
            Cancel
          </button>
          <button
            on:click={createFolder}
            class="px-4 py-2 bg-blue-600 text-white text-sm font-medium rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-300 disabled:opacity-50"
            disabled={creating || !folderName.trim()}
          >
            {#if creating}
              <div class="flex items-center">
                <div class="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                Creating...
              </div>
            {:else}
              Create Folder
            {/if}
          </button>
        </div>
      </div>
    </div>
  </div>
{/if}
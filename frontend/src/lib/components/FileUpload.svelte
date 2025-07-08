<script>
  import { createEventDispatcher } from 'svelte';
  import { api } from '$lib/api.js';
  import { validateFile } from '$lib/utils.js';

  const dispatch = createEventDispatcher();

  export let currentFolder = null;

  let dragActive = false;
  let uploading = false;
  let uploadMessage = '';
  let fileInput;

  function handleDrop(e) {
    e.preventDefault();
    dragActive = false;
    
    const files = e.dataTransfer.files;
    if (files.length > 0) {
      uploadFiles(files);
    }
  }

  function handleDragOver(e) {
    e.preventDefault();
    dragActive = true;
  }

  function handleDragLeave(e) {
    e.preventDefault();
    dragActive = false;
  }

  function handleFileSelect(e) {
    const files = e.target.files;
    if (files.length > 0) {
      uploadFiles(files);
    }
  }

  async function uploadFiles(files) {
    uploading = true;
    uploadMessage = '';

    try {
      let successCount = 0;
      let failedFiles = [];

      for (let file of files) {
        try {
          // Validate file before upload
          const validation = validateFile(file);
          if (!validation.valid) {
            failedFiles.push(`${file.name}: ${validation.error}`);
            continue;
          }

          console.log('FileUpload Component - Uploading file to folder:', currentFolder);
          console.log('File:', file.name, 'Size:', file.size);
          
          const result = await api.uploadFile(file, currentFolder);
          console.log('Upload result:', result);
          
          successCount++;
        } catch (error) {
          failedFiles.push(`${file.name}: ${error.message}`);
        }
      }

      if (successCount > 0) {
        const folderText = currentFolder ? ' to current folder' : '';
        uploadMessage = `Successfully uploaded ${successCount} file(s)${folderText}`;
        dispatch('fileUploaded');
      }
      
      if (failedFiles.length > 0) {
        uploadMessage += failedFiles.length > 0 ? `\nFailed: ${failedFiles.join(', ')}` : '';
      }
      
      // Clear the file input
      if (fileInput) {
        fileInput.value = '';
      }
    } catch (error) {
      uploadMessage = `Upload failed: ${error.message}`;
    } finally {
      uploading = false;
      
      // Clear message after 5 seconds
      setTimeout(() => {
        uploadMessage = '';
      }, 5000);
    }
  }

  function triggerFileInput() {
    fileInput.click();
  }

  // Show current folder in upload area
  $: folderDisplayText = currentFolder ? 'Upload to current folder' : 'Upload files here';
</script>

<div class="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
  <h2 class="text-lg font-semibold text-gray-900 mb-4">Upload Files</h2>
  
  <div
    class="border-2 border-dashed rounded-lg p-8 text-center transition-colors duration-200 {dragActive ? 'border-blue-400 bg-blue-50' : 'border-gray-300 hover:border-gray-400'}"
    on:drop={handleDrop}
    on:dragover={handleDragOver}
    on:dragleave={handleDragLeave}
    role="button"
    tabindex="0"
    on:click={triggerFileInput}
    on:keydown={(e) => e.key === 'Enter' && triggerFileInput()}
  >
    {#if uploading}
      <div class="flex flex-col items-center">
        <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mb-2"></div>
        <p class="text-sm text-gray-600">Uploading files...</p>
      </div>
    {:else}
      <svg class="mx-auto h-12 w-12 text-gray-400 mb-4" stroke="currentColor" fill="none" viewBox="0 0 48 48">
        <path d="M28 8H12a4 4 0 00-4 4v20m32-12v8m0 0v8a4 4 0 01-4 4H12a4 4 0 01-4-4v-4m32-4l-3.172-3.172a4 4 0 00-5.656 0L28 28M8 32l9.172-9.172a4 4 0 015.656 0L28 28m0 0l4 4m4-24h8m-4-4v8m-12 4h.02" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" />
      </svg>
      <p class="text-lg text-gray-600 mb-2">
        {dragActive ? 'Drop files here' : folderDisplayText}
      </p>
      <p class="text-sm text-gray-500 mb-4">or click to browse</p>
      <button
        type="button"
        class="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
        on:click|stopPropagation={triggerFileInput}
      >
        Choose Files
      </button>
    {/if}
  </div>

  <input
    bind:this={fileInput}
    type="file"
    multiple
    class="hidden"
    on:change={handleFileSelect}
  />

  {#if uploadMessage}
    <div class="mt-4 p-3 rounded-md {uploadMessage.includes('failed') ? 'bg-red-50 text-red-700' : 'bg-green-50 text-green-700'}">
      <pre class="whitespace-pre-wrap text-sm">{uploadMessage}</pre>
    </div>
  {/if}
</div>
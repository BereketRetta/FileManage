<script>
  import { onMount } from "svelte";
  import { goto } from "$app/navigation";
  import FileUpload from "$lib/components/FileUpload.svelte";
  import FileList from "$lib/components/FileList.svelte";
  import FolderBreadcrumb from "$lib/components/FolderBreadcrumb.svelte";
  import CreateFolderModal from "$lib/components/CreateFolderModal.svelte";
  import SearchBar from "$lib/components/SearchBar.svelte";
  import { fileStore } from "$lib/stores/fileStore.js";
  import {
    currentFolderId,
    breadcrumb,
    itemsStore,
  } from "$lib/stores/folderStore.js";
  import { isAuthenticated, logout, user } from "$lib/stores/authStore.js";
  import { api } from "$lib/api.js";
  import AuthGuard from "$lib/components/AuthGuard.svelte";

  let items = [];
  let loading = true;
  let error = null;
  let showCreateFolder = false;
  let currentFolder = null;
  let breadcrumbPath = [];
  let searchQuery = "";
  let sortBy = "name";
  let sortOrder = "asc";

  // Check authentication on mount
  onMount(() => {
    isAuthenticated.subscribe((auth) => {
      if (!auth) {
        goto("/auth");
        return;
      }
      loadItems();
    });
  });

  // Subscribe to folder changes
  currentFolderId.subscribe(async (folderId) => {
    currentFolder = folderId;
    if ($isAuthenticated) {
      await loadItems();
      if (folderId) {
        await loadBreadcrumb(folderId);
      } else {
        breadcrumbPath = [{ folder_id: null, name: "Home" }];
      }
    }
  });

  async function loadItems() {
    try {
      loading = true;
      error = null;
      const response = await api.getItems(currentFolder);
      items = response.items || [];
      itemsStore.set(items);
    } catch (err) {
      error = err.message;
      console.error("Error loading items:", err);

      // If unauthorized, redirect to auth
      if (err.message.includes("401") || err.message.includes("Unauthorized")) {
        goto("/auth");
      }
    } finally {
      loading = false;
    }
  }

  async function loadBreadcrumb(folderId) {
    try {
      const response = await api.getFolderBreadcrumb(folderId);
      breadcrumbPath = response.breadcrumb || [];
      breadcrumb.set(breadcrumbPath);
    } catch (err) {
      console.error("Error loading breadcrumb:", err);
    }
  }

  function handleFileUploaded() {
    loadItems();
  }

  function handleFileDeleted() {
    loadItems();
  }

  function handleFileUpdated() {
    loadItems();
  }

  function handleFolderCreated() {
    loadItems();
  }

  function handleNavigate(event) {
    currentFolderId.set(event.detail.folderId);
  }

  function handleFolderOpen(event) {
    currentFolderId.set(event.detail.folderId);
  }

  function openCreateFolderModal() {
    showCreateFolder = true;
  }

  function handleSearch(event) {
    searchQuery = event.detail.query;
  }

  function handleSort(event) {
    sortBy = event.detail.sortBy;
    sortOrder = event.detail.sortOrder;
  }

  function handleLogout() {
    logout();
    goto("/auth");
  }

  // Filter and sort items
  $: filteredItems = items
    .filter(
      (item) =>
        searchQuery === "" ||
        item.name.toLowerCase().includes(searchQuery.toLowerCase())
    )
    .sort((a, b) => {
      // Always show folders first
      if (a.item_type === "folder" && b.item_type === "file") return -1;
      if (a.item_type === "file" && b.item_type === "folder") return 1;

      let aVal = a[sortBy];
      let bVal = b[sortBy];

      if (sortBy === "upload_date" || sortBy === "created_date") {
        aVal = new Date(aVal || 0);
        bVal = new Date(bVal || 0);
      } else if (sortBy === "size") {
        aVal = a.size || 0;
        bVal = b.size || 0;
      } else {
        aVal = String(aVal || "").toLowerCase();
        bVal = String(bVal || "").toLowerCase();
      }

      if (sortOrder === "asc") {
        return aVal > bVal ? 1 : -1;
      } else {
        return aVal < bVal ? 1 : -1;
      }
    });
</script>

<svelte:head>
  <title>File Manager</title>
</svelte:head>

<AuthGuard>
  <div class="container mx-auto px-4 py-8 max-w-6xl">
    <header class="mb-8">
      <div class="flex justify-between items-center">
        <div>
          <h1 class="text-3xl font-bold text-gray-900 mb-2">File Manager</h1>
          <p class="text-gray-600">Upload, manage, and organize your files</p>
        </div>
        
        <!-- User Info & Logout -->
        <div class="flex items-center space-x-4">
          <p class="text-gray-600">Hi {$user.full_name}</p>
          <button
            on:click={handleLogout}
            class="text-sm text-gray-500 hover:text-gray-700 px-3 py-2 rounded-md border border-gray-300 hover:bg-gray-50"
          >
            Logout
          </button>
        </div>
      </div>
    </header>

    <!-- Breadcrumb Navigation -->
    <FolderBreadcrumb
      breadcrumb={breadcrumbPath}
      on:navigate={handleNavigate}
    />

    <!-- Search and Controls -->
    <div
      class="flex flex-col sm:flex-row justify-between items-center mb-6 space-y-4 sm:space-y-0"
    >
      <SearchBar on:search={handleSearch} />

      <div class="flex space-x-2">
        <button
          on:click={openCreateFolderModal}
          class="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-green-600 hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500"
        >
          <svg
            class="w-4 h-4 mr-2"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              stroke-linecap="round"
              stroke-linejoin="round"
              stroke-width="2"
              d="M12 6v6m0 0v6m0-6h6m-6 0H6"
            />
          </svg>
          New Folder
        </button>
      </div>
    </div>

    <!-- Search Results Indicator -->
    {#if searchQuery}
      <div class="mb-4 p-3 bg-blue-50 border border-blue-200 rounded-md">
        <div class="flex items-center justify-between">
          <div class="flex items-center">
            <svg
              class="h-5 w-5 text-blue-400 mr-2"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                stroke-linecap="round"
                stroke-linejoin="round"
                stroke-width="2"
                d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"
              />
            </svg>
            <p class="text-sm text-blue-700">
              Searching for "<span class="font-medium">{searchQuery}</span>" -
              Found {filteredItems.length} result{filteredItems.length !== 1
                ? "s"
                : ""}
            </p>
          </div>
          <button
            on:click={() => {
              searchQuery = "";
              loadItems();
            }}
            class="text-blue-400 hover:text-blue-600"
            title="Clear search"
          >
            <svg
              class="h-4 w-4"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                stroke-linecap="round"
                stroke-linejoin="round"
                stroke-width="2"
                d="M6 18L18 6M6 6l12 12"
              />
            </svg>
          </button>
        </div>
      </div>
    {/if}

    <div class="space-y-8">
      <FileUpload {currentFolder} on:fileUploaded={handleFileUploaded} />

      {#if error}
        <div class="bg-red-50 border border-red-200 rounded-md p-4">
          <div class="flex">
            <div class="flex-shrink-0">
              <svg
                class="h-5 w-5 text-red-400"
                viewBox="0 0 20 20"
                fill="currentColor"
              >
                <path
                  fill-rule="evenodd"
                  d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z"
                  clip-rule="evenodd"
                />
              </svg>
            </div>
            <div class="ml-3">
              <h3 class="text-sm font-medium text-red-800">Error</h3>
              <p class="text-sm text-red-700 mt-1">{error}</p>
            </div>
          </div>
        </div>
      {/if}

      {#if loading}
        <div class="flex justify-center items-center py-12">
          <div
            class="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"
          ></div>
          <span class="ml-2 text-gray-600">Loading...</span>
        </div>
      {:else}
        <FileList
          items={filteredItems}
          on:fileDeleted={handleFileDeleted}
          on:fileUpdated={handleFileUpdated}
          on:folderOpen={handleFolderOpen}
          on:sort={handleSort}
        />
      {/if}
    </div>

    <!-- Create Folder Modal -->
    <CreateFolderModal
      bind:show={showCreateFolder}
      currentFolderId={currentFolder}
      on:folderCreated={handleFolderCreated}
    />
  </div>
</AuthGuard>

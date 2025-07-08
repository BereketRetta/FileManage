<script>
  import { onMount } from "svelte";
  import { goto } from "$app/navigation";
  import { isAuthenticated, logout } from "$lib/stores/authStore.js";
  import { api } from "$lib/api.js";

  let loading = true;
  let authChecked = false;

  onMount(async () => {
    await checkAuthentication();
  });

  async function checkAuthentication() {
    loading = true;

    try {
      // Check if we have a token
      const token = localStorage.getItem("auth_token");
      if (!token) {
        console.log("No token found, redirecting to auth");
        goto("/auth");
        return;
      }

      // Validate the token by making an API call
      const userData = await api.getCurrentUser(token);

      // If we get here, the token is valid
      console.log("Token validated, user authenticated");
      authChecked = true;
    } catch (error) {
      console.log("Authentication check failed:", error.message);

      // Token is invalid or expired, clear auth and redirect
      logout();
      goto("/auth");
    } finally {
      loading = false;
    }
  }

  // Show loading spinner while checking auth
  $: if (loading) {
    // Don't render slot content while checking
  }
</script>

{#if loading}
  <div class="min-h-screen bg-gray-50 flex items-center justify-center">
    <div class="text-center">
      <div
        class="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"
      ></div>
      <p class="text-gray-600">Checking authentication...</p>
    </div>
  </div>
{:else if authChecked && $isAuthenticated}
  <slot />
{:else}
  <div class="min-h-screen bg-gray-50 flex items-center justify-center">
    <div class="text-center">
      <p class="text-gray-600 mb-4">Redirecting to login...</p>
      <div class="animate-pulse h-4 bg-gray-300 rounded w-32 mx-auto"></div>
    </div>
  </div>
{/if}

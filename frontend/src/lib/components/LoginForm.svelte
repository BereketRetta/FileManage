<script>
  import { createEventDispatcher } from 'svelte';
  import { api } from '$lib/api.js';
  import { login } from '$lib/stores/authStore.js';

  const dispatch = createEventDispatcher();

  let email = '';
  let password = '';
  let loading = false;
  let error = '';

  async function handleLogin() {
    if (!email || !password) {
      error = 'Please fill in all fields';
      return;
    }

    loading = true;
    error = '';

    try {
      const response = await api.login({ email, password });
      const userData = await api.getCurrentUser(response.access_token);
      
      login(response.access_token, userData);
      dispatch('success');
    } catch (err) {
      error = err.message;
    } finally {
      loading = false;
    }
  }

  function switchToRegister() {
    dispatch('switchToRegister');
  }
</script>

<div class="w-full max-w-md">
  <form on:submit|preventDefault={handleLogin} class="bg-white shadow-md rounded px-8 pt-6 pb-8 mb-4">
    <div class="mb-6">
      <h2 class="text-2xl font-bold text-center text-gray-900 mb-2">Sign In</h2>
      <p class="text-center text-gray-600">Access your file manager</p>
    </div>

    {#if error}
      <div class="mb-4 p-3 bg-red-50 border border-red-200 rounded-md">
        <p class="text-sm text-red-700">{error}</p>
      </div>
    {/if}

    <div class="mb-4">
      <label class="block text-gray-700 text-sm font-bold mb-2" for="email">
        Email
      </label>
      <input
        id="email"
        type="email"
        bind:value={email}
        placeholder="Enter your email"
        class="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:ring-2 focus:ring-blue-500"
        disabled={loading}
        required
      />
    </div>

    <div class="mb-6">
      <label class="block text-gray-700 text-sm font-bold mb-2" for="password">
        Password
      </label>
      <input
        id="password"
        type="password"
        bind:value={password}
        placeholder="Enter your password"
        class="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 mb-3 leading-tight focus:outline-none focus:ring-2 focus:ring-blue-500"
        disabled={loading}
        required
      />
    </div>

    <div class="flex flex-col space-y-4">
      <button
        type="submit"
        class="bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded focus:outline-none focus:shadow-outline disabled:opacity-50"
        disabled={loading}
      >
        {#if loading}
          <div class="flex items-center justify-center">
            <div class="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
            Signing In...
          </div>
        {:else}
          Sign In
        {/if}
      </button>

      <button
        type="button"
        on:click={switchToRegister}
        class="text-blue-500 hover:text-blue-700 text-sm font-medium"
        disabled={loading}
      >
        Don't have an account? Sign up
      </button>
    </div>
  </form>
</div>
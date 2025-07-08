<script>
  import { createEventDispatcher } from 'svelte';
  import { api } from '$lib/api.js';

  const dispatch = createEventDispatcher();

  let email = '';
  let password = '';
  let confirmPassword = '';
  let fullName = '';
  let loading = false;
  let error = '';
  let success = false;

  async function handleRegister() {
    if (!email || !password || !fullName) {
      error = 'Please fill in all fields';
      return;
    }

    if (password !== confirmPassword) {
      error = 'Passwords do not match';
      return;
    }

    if (password.length < 6) {
      error = 'Password must be at least 6 characters long';
      return;
    }

    loading = true;
    error = '';

    try {
      await api.register({
        email,
        password,
        full_name: fullName
      });
      
      success = true;
      
      // Auto-switch to login after 2 seconds
      setTimeout(() => {
        dispatch('switchToLogin');
      }, 2000);
      
    } catch (err) {
      error = err.message;
    } finally {
      loading = false;
    }
  }

  function switchToLogin() {
    dispatch('switchToLogin');
  }
</script>

<div class="w-full max-w-md">
  <form on:submit|preventDefault={handleRegister} class="bg-white shadow-md rounded px-8 pt-6 pb-8 mb-4">
    <div class="mb-6">
      <h2 class="text-2xl font-bold text-center text-gray-900 mb-2">Sign Up</h2>
      <p class="text-center text-gray-600">Create your file manager account</p>
    </div>

    {#if error}
      <div class="mb-4 p-3 bg-red-50 border border-red-200 rounded-md">
        <p class="text-sm text-red-700">{error}</p>
      </div>
    {/if}

    {#if success}
      <div class="mb-4 p-3 bg-green-50 border border-green-200 rounded-md">
        <p class="text-sm text-green-700">Account created successfully! Redirecting to login...</p>
      </div>
    {/if}

    <div class="mb-4">
      <label class="block text-gray-700 text-sm font-bold mb-2" for="fullName">
        Full Name
      </label>
      <input
        id="fullName"
        type="text"
        bind:value={fullName}
        placeholder="Enter your full name"
        class="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:ring-2 focus:ring-blue-500"
        disabled={loading || success}
        required
      />
    </div>

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
        disabled={loading || success}
        required
      />
    </div>

    <div class="mb-4">
      <label class="block text-gray-700 text-sm font-bold mb-2" for="password">
        Password
      </label>
      <input
        id="password"
        type="password"
        bind:value={password}
        placeholder="Enter your password"
        class="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:ring-2 focus:ring-blue-500"
        disabled={loading || success}
        required
      />
    </div>

    <div class="mb-6">
      <label class="block text-gray-700 text-sm font-bold mb-2" for="confirmPassword">
        Confirm Password
      </label>
      <input
        id="confirmPassword"
        type="password"
        bind:value={confirmPassword}
        placeholder="Confirm your password"
        class="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 mb-3 leading-tight focus:outline-none focus:ring-2 focus:ring-blue-500"
        disabled={loading || success}
        required
      />
    </div>

    <div class="flex flex-col space-y-4">
      <button
        type="submit"
        class="bg-green-500 hover:bg-green-700 text-white font-bold py-2 px-4 rounded focus:outline-none focus:shadow-outline disabled:opacity-50"
        disabled={loading || success}
      >
        {#if loading}
          <div class="flex items-center justify-center">
            <div class="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
            Creating Account...
          </div>
        {:else}
          Sign Up
        {/if}
      </button>

      <button
        type="button"
        on:click={switchToLogin}
        class="text-blue-500 hover:text-blue-700 text-sm font-medium"
        disabled={loading}
      >
        Already have an account? Sign in
      </button>
    </div>
  </form>
</div>
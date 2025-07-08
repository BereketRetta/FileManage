<script>
  import { goto } from '$app/navigation';
  import { onMount } from 'svelte';
  import LoginForm from '$lib/components/LoginForm.svelte';
  import RegisterForm from '$lib/components/RegisterForm.svelte';
  import { isAuthenticated } from '$lib/stores/authStore.js';

  let showLogin = true;

  // Redirect if already authenticated
  onMount(() => {
    isAuthenticated.subscribe(auth => {
      if (auth) {
        goto('/');
      }
    });
  });

  function handleLoginSuccess() {
    goto('/');
  }

  function switchToRegister() {
    showLogin = false;
  }

  function switchToLogin() {
    showLogin = true;
  }
</script>

<svelte:head>
  <title>{showLogin ? 'Sign In' : 'Sign Up'} - File Manager</title>
</svelte:head>

<div class="min-h-screen bg-gray-50 flex flex-col justify-center py-12 sm:px-6 lg:px-8">
  <div class="sm:mx-auto sm:w-full sm:max-w-md">
    <div class="text-center">
      <h1 class="text-3xl font-bold text-gray-900 mb-2">File Manager</h1>
      <p class="text-gray-600">Secure cloud storage for your files</p>
    </div>
  </div>

  <div class="mt-8 sm:mx-auto sm:w-full sm:max-w-md">
    {#if showLogin}
      <LoginForm 
        on:success={handleLoginSuccess}
        on:switchToRegister={switchToRegister}
      />
    {:else}
      <RegisterForm 
        on:switchToLogin={switchToLogin}
      />
    {/if}
  </div>
</div>
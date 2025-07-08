import { writable } from 'svelte/store';
import { browser } from '$app/environment';

// Auth store
export const isAuthenticated = writable(false);
export const user = writable(null);
export const token = writable(null);
export const authLoading = writable(false);

// Initialize auth state from localStorage on browser
if (browser) {
  const storedToken = localStorage.getItem('auth_token');
  const storedUser = localStorage.getItem('auth_user');
  
  if (storedToken && storedUser) {
    try {
      const userData = JSON.parse(storedUser);
      token.set(storedToken);
      user.set(userData);
      isAuthenticated.set(true);
    } catch (error) {
      console.error('Error parsing stored user data:', error);
      // Clear invalid data
      localStorage.removeItem('auth_token');
      localStorage.removeItem('auth_user');
    }
  }
}

// Auth functions
export function login(authToken, userData) {
  if (browser) {
    localStorage.setItem('auth_token', authToken);
    localStorage.setItem('auth_user', JSON.stringify(userData));
  }
  
  token.set(authToken);
  user.set(userData);
  isAuthenticated.set(true);
}

export function logout() {
  if (browser) {
    localStorage.removeItem('auth_token');
    localStorage.removeItem('auth_user');
  }
  
  token.set(null);
  user.set(null);
  isAuthenticated.set(false);
}

export function updateUser(userData) {
  if (browser) {
    localStorage.setItem('auth_user', JSON.stringify(userData));
  }
  user.set(userData);
}

export function getAuthHeaders() {
  let authToken;
  token.subscribe(t => authToken = t)();
  
  return authToken ? {
    'Authorization': `Bearer ${authToken}`,
    'Content-Type': 'application/json'
  } : {
    'Content-Type': 'application/json'
  };
}

export function getToken() {
  if (browser) {
    return localStorage.getItem('auth_token');
  }
  return null;
}

export function isTokenValid() {
  const authToken = getToken();
  if (!authToken) return false;
  
  try {
    // Basic JWT token validation (check if it's not expired)
    const payload = JSON.parse(atob(authToken.split('.')[1]));
    const currentTime = Math.floor(Date.now() / 1000);
    return payload.exp > currentTime;
  } catch (error) {
    return false;
  }
}

// Auto-logout when token expires
if (browser) {
  // Check token validity every minute
  setInterval(() => {
    const authToken = getToken();
    if (authToken && !isTokenValid()) {
      console.log('Token expired, logging out...');
      logout();
      // Redirect to auth page if we're not already there
      if (window.location.pathname !== '/auth') {
        window.location.href = '/auth';
      }
    }
  }, 60000); // Check every minute
}
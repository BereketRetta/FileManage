const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

// Get auth headers for authenticated requests
function getAuthHeaders() {
  const token = localStorage.getItem('auth_token');
  return {
    'Content-Type': 'application/json',
    ...(token && { 'Authorization': `Bearer ${token}` })
  };
}

// Handle API errors consistently
async function handleResponse(response) {
  if (!response.ok) {
    let errorMessage = 'An error occurred';
    try {
      const errorData = await response.json();
      errorMessage = errorData.detail || errorData.message || `HTTP ${response.status}`;
    } catch {
      errorMessage = `HTTP ${response.status}: ${response.statusText}`;
    }
    
    // Handle auth errors
    if (response.status === 401 || response.status === 403) {

      const { logout } = await import('$lib/stores/authStore.js');
      logout();
  
      if (typeof window !== 'undefined' && window.location.pathname !== '/auth') {
        window.location.href = '/auth';
      }
    }
    
    throw new Error(errorMessage);
  }
  return response.json();
}

export const api = {
  async register(userData) {
    const response = await fetch(`${API_BASE_URL}/api/auth/register`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        email: userData.email.toLowerCase().trim(),
        password: userData.password,
        full_name: userData.full_name.trim()
      })
    });

    return handleResponse(response);
  },

  async login(credentials) {
    const response = await fetch(`${API_BASE_URL}/api/auth/login`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        email: credentials.email.toLowerCase().trim(),
        password: credentials.password
      })
    });

    const data = await handleResponse(response);
    
    if (data.access_token) {
      localStorage.setItem('auth_token', data.access_token);
    }
    
    return data;
  },

  async getCurrentUser(token = null) {
    const authToken = token || localStorage.getItem('auth_token');
    
    if (!authToken) {
      throw new Error('No authentication token found');
    }

    const response = await fetch(`${API_BASE_URL}/api/auth/me`, {
      headers: {
        'Authorization': `Bearer ${authToken}`,
        'Content-Type': 'application/json',
      }
    });

    return handleResponse(response);
  },

  // Logout
  logout() {
    localStorage.removeItem('auth_token');
    localStorage.removeItem('auth_user');
  },

  // Check if Autheticated
  isAuthenticated() {
    const token = localStorage.getItem('auth_token');
    return !!token;
  },

//  Validate and Refresh User
  async validateAndRefreshUser() {
    try {
      if (!this.isAuthenticated()) {
        return null;
      }
      
      const userData = await this.getCurrentUser();
      localStorage.setItem('auth_user', JSON.stringify(userData));
      return userData;
    } catch (error) {
      // Token is invalid
      this.logout();
      return null;
    }
  },

  // Upload File
  async uploadFile(file, folderId = null) {
    const token = localStorage.getItem('auth_token');
    if (!token) {
      throw new Error('Authentication required');
    }

    console.log('API Upload - File:', file.name, 'Folder ID:', folderId);

    const formData = new FormData();
    formData.append('file', file);
    
    // Only append folder_id if it's not null/undefined
    if (folderId) {
      formData.append('folder_id', folderId);
      console.log('Added folder_id to FormData:', folderId);
    }

    const response = await fetch(`${API_BASE_URL}/api/files/upload`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`
        // Don't set Content-Type for FormData - let browser set it
      },
      body: formData
    });

    return handleResponse(response);
  },

  // Get all items in user's root folder
  async getItems(folderId = null, searchQuery = null) {
    const url = new URL(`${API_BASE_URL}/api/files`);
    if (folderId) {
      url.searchParams.append('folder_id', folderId);
    }
    if (searchQuery && searchQuery.trim()) {
      url.searchParams.append('search', searchQuery.trim());
    }
    
    const response = await fetch(url, {
      headers: getAuthHeaders()
    });
    
    return handleResponse(response);
  },

  // Download
  async downloadFile(fileId, filename) {
    const token = localStorage.getItem('auth_token');
    if (!token) {
      throw new Error('Authentication required');
    }

    const response = await fetch(`${API_BASE_URL}/api/files/${fileId}/download`, {
      headers: {
        'Authorization': `Bearer ${token}`
      }
    });
    
    if (!response.ok) {
      throw new Error('Failed to download file');
    }
    
    const blob = await response.blob();
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.style.display = 'none';
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    window.URL.revokeObjectURL(url);
    document.body.removeChild(a);
  },

  // Update file name
  async updateFile(fileId, data) {
    const response = await fetch(`${API_BASE_URL}/api/files/${fileId}`, {
      method: 'PUT',
      headers: getAuthHeaders(),
      body: JSON.stringify(data)
    });

    return handleResponse(response);
  },

  // Delete
  async deleteFile(fileId) {
    const response = await fetch(`${API_BASE_URL}/api/files/${fileId}`, {
      method: 'DELETE',
      headers: getAuthHeaders()
    });

    return handleResponse(response);
  },

  // Create Folder
  async createFolder(folderData) {
    const response = await fetch(`${API_BASE_URL}/api/folders`, {
      method: 'POST',
      headers: getAuthHeaders(),
      body: JSON.stringify({
        name: folderData.name.trim(),
        parent_folder_id: folderData.parent_folder_id || null
      })
    });

    return handleResponse(response);
  },

  // Update Folder name
  async updateFolder(folderId, data) {
    const response = await fetch(`${API_BASE_URL}/api/folders/${folderId}`, {
      method: 'PUT',
      headers: getAuthHeaders(),
      body: JSON.stringify({
        name: data.name.trim()
      })
    });

    return handleResponse(response);
  },

  // Delete folder if not empty
  async deleteFolder(folderId) {
    const response = await fetch(`${API_BASE_URL}/api/folders/${folderId}`, {
      method: 'DELETE',
      headers: getAuthHeaders()
    });

    return handleResponse(response);
  },

  // Get folder breadcrumb
  async getFolderBreadcrumb(folderId) {
    const response = await fetch(`${API_BASE_URL}/api/folders/${folderId}/breadcrumb`, {
      headers: getAuthHeaders()
    });
    
    return handleResponse(response);
  },
};
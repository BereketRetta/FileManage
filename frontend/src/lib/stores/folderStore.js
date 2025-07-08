import { writable } from 'svelte/store';

export const currentFolderId = writable(null);
export const breadcrumb = writable([{ folder_id: null, name: 'Home' }]);
export const itemsStore = writable([]);

// Navigation functions
export function navigateToFolder(folderId) {
  currentFolderId.set(folderId);
}

export function navigateToRoot() {
  currentFolderId.set(null);
  breadcrumb.set([{ folder_id: null, name: 'Home' }]);
}
import { writable } from 'svelte/store';

export const notificationsWindowOpen = writable(false);
export const unreadNotificationCount = writable(0);

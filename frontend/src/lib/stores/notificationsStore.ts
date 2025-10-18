import { writable } from 'svelte/store';

export interface Notification {
	id: number;
	user_id: number;
	type: string;
	message: string;
	data: any;
	is_read: boolean;
	created_at: string;
}

export const notificationsWindowOpen = writable(false);
export const unreadNotificationCount = writable(0);
export const notifications = writable<Notification[]>([]);

// Function to add a new notification to the store
export function addNotification(notification: Notification) {
	notifications.update(current => {
		// Check if notification already exists (avoid duplicates)
		const exists = current.some(n => n.id === notification.id);
		if (exists) {
			return current;
		}
		// Add new notification to the beginning of the array
		return [notification, ...current];
	});

	// Update unread count if notification is unread
	if (!notification.is_read) {
		unreadNotificationCount.update(count => count + 1);
	}
}

// Function to set all notifications (when fetching from API)
export function setNotifications(newNotifications: Notification[]) {
	notifications.set(newNotifications);
	const unreadCount = newNotifications.filter(n => !n.is_read).length;
	unreadNotificationCount.set(unreadCount);
}

// Function to mark all notifications as read
export function markAllAsRead() {
	notifications.update(current =>
		current.map(n => ({ ...n, is_read: true }))
	);
	unreadNotificationCount.set(0);
}

// Function to clear all notifications
export function clearAllNotifications() {
	notifications.set([]);
	unreadNotificationCount.set(0);
}

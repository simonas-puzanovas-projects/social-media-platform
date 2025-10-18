import { writable } from 'svelte/store';

// Track if there are any unread messages
export const hasUnreadMessages = writable(false);

// Function to fetch unread message status from API
export async function fetchUnreadMessageStatus() {
	try {
		const response = await fetch('http://localhost:5000/api/friend_list', {
			credentials: 'include'
		});

		if (!response.ok) {
			return;
		}

		const data = await response.json();
		const hasUnread = data.some((friend: any) => (friend.unread_count || 0) > 0);
		hasUnreadMessages.set(hasUnread);
	} catch (error) {
		console.error('Error fetching unread message status:', error);
	}
}

// Function to update unread status when a new message is received
export function handleNewMessage(senderId: number, selectedContactId: number | null) {
	// If the message is not from the currently selected contact, mark as unread
	if (selectedContactId !== senderId) {
		hasUnreadMessages.set(true);
	}
}

// Function to mark messages as read
export function handleMessagesRead() {
	// Re-fetch to get accurate unread count
	fetchUnreadMessageStatus();
}

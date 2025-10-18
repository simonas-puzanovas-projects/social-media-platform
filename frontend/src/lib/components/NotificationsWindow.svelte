<script lang="ts">
	import { onMount } from 'svelte';
	import { notificationsWindowOpen, unreadNotificationCount, notifications, setNotifications, markAllAsRead, clearAllNotifications, type Notification } from '$lib/stores/notificationsStore';

	let activeTab = 'all';
	let loading = false;
	let error = '';
	let successMessage = '';

	async function fetchNotifications() {
		try {
			loading = true;
			error = '';
			const response = await fetch('http://localhost:5000/notifications', {
				credentials: 'include'
			});
			if (!response.ok) throw new Error('Failed to fetch notifications');
			const fetchedNotifications = await response.json();

			// Update the store with fetched notifications
			setNotifications(fetchedNotifications);

			loading = false;
		} catch (err) {
			error = err instanceof Error ? err.message : 'An error occurred';
			loading = false;
		}
	}

	async function cleanupNotifications() {
		try {
			await fetch('http://localhost:5000/cleanup_notifications', {
				method: 'POST',
				credentials: 'include'
			});
		} catch (err) {
			console.error('Failed to cleanup notifications:', err);
		}
	}

	async function markNotificationsAsRead() {
		try {
			await fetch('http://localhost:5000/mark_notifications_read', {
				method: 'POST',
				credentials: 'include'
			});
			// Update local store to mark all as read
			markAllAsRead();
		} catch (err) {
			console.error('Failed to mark notifications as read:', err);
		}
	}

	async function respondToFriendRequest(friendshipId: number, response: string) {
		try {
			const res = await fetch('http://localhost:5000/respond_friend_request', {
				method: 'POST',
				credentials: 'include',
				headers: { 'Content-Type': 'application/json' },
				body: JSON.stringify({ friendship_id: friendshipId, response })
			});
			const data = await res.json();
			if (data.success) {
				successMessage = data.message;
				setTimeout(() => successMessage = '', 3000);
				await fetchNotifications();
			} else {
				error = data.message;
			}
		} catch (err) {
			error = err instanceof Error ? err.message : 'An error occurred';
		}
	}

	async function clearNotifications() {
		try {
			const response = await fetch('http://localhost:5000/clear_notifications', {
				method: 'POST',
				credentials: 'include'
			});
			const data = await response.json();
			if (data.success) {
				clearAllNotifications();
				successMessage = `Cleared ${data.deleted_count} notification${data.deleted_count !== 1 ? 's' : ''}`;
				setTimeout(() => successMessage = '', 3000);
			} else {
				error = 'Failed to clear notifications';
			}
		} catch (err) {
			error = err instanceof Error ? err.message : 'An error occurred';
		}
	}

	function switchTab(tab: string) {
		activeTab = tab;
		error = '';
		successMessage = '';
	}

	function formatDate(dateString: string) {
		const date = new Date(dateString);
		const now = new Date();
		const diff = now.getTime() - date.getTime();
		const minutes = Math.floor(diff / (1000 * 60));
		const hours = Math.floor(diff / (1000 * 60 * 60));
		const days = Math.floor(diff / (1000 * 60 * 60 * 24));

		if (minutes < 1) return 'Just now';
		if (minutes < 60) return `${minutes}m ago`;
		if (hours < 24) return `${hours}h ago`;
		if (days === 1) return 'Yesterday';
		if (days < 7) return `${days}d ago`;
		return date.toLocaleDateString();
	}

	function getFriendRequestInfo(notification: Notification) {
		if (notification.type !== 'friend_request') return null;

		const data = typeof notification.data === 'string'
			? JSON.parse(notification.data)
			: notification.data;

		return {
			username: data.requester_username || data.username || 'Unknown',
			friendshipId: data.friendship_id
		};
	}

	$: filteredNotifications = activeTab === 'all'
		? $notifications
		: $notifications.filter(n => n.type === 'friend_request');

	$: if ($notificationsWindowOpen) {
		fetchNotifications();
		cleanupNotifications();
		markNotificationsAsRead();
	}

	onMount(() => {
		fetchNotifications();
	});
</script>

{#if $notificationsWindowOpen}
	<div class="fixed inset-0 backdrop-blur-sm bg-black/30 z-50 flex items-center justify-center md:p-4" on:click={() => notificationsWindowOpen.set(false)}>
		<div class="bg-white md:rounded-lg shadow-xl w-full h-full md:w-[600px] md:h-[700px] md:max-h-[90vh] flex flex-col" on:click|stopPropagation>
			<!-- Header -->
			<div class="px-6 py-4 border-b border-gray-200 flex items-center justify-between">
				<h1 class="text-xl font-semibold text-gray-900">Notifications</h1>
				<div class="flex items-center gap-2">
					{#if $notifications.length > 0}
						<button on:click={clearNotifications} class="px-3 py-1.5 text-sm font-medium text-red-600 hover:text-red-700 hover:bg-red-50 rounded-md transition-colors">
							Clear all
						</button>
					{/if}
					<button on:click={() => notificationsWindowOpen.set(false)} class="text-gray-400 hover:text-gray-600">
						<svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
							<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/>
						</svg>
					</button>
				</div>
			</div>

			<!-- Tabs -->
			<div class="px-6 py-4 border-b border-gray-200">
				<div class="flex gap-4">
					<button on:click={() => switchTab('all')} class="pb-2 px-1 text-sm font-medium transition-colors {activeTab === 'all' ? 'text-gray-900 border-b-2 border-gray-900' : 'text-gray-500 hover:text-gray-700'}">
						All {$notifications.length > 0 ? `(${$notifications.length})` : ''}
					</button>
					<button on:click={() => switchTab('friend_requests')} class="pb-2 px-1 text-sm font-medium transition-colors {activeTab === 'friend_requests' ? 'text-gray-900 border-b-2 border-gray-900' : 'text-gray-500 hover:text-gray-700'}">
						Friend Requests {$notifications.filter(n => n.type === 'friend_request').length > 0 ? `(${$notifications.filter(n => n.type === 'friend_request').length})` : ''}
					</button>
				</div>
			</div>

			{#if error}
				<div class="mx-6 mt-3 p-3 bg-red-50 border border-red-200 rounded-md">
					<p class="text-xs text-red-800">{error}</p>
				</div>
			{/if}
			{#if successMessage}
				<div class="mx-6 mt-3 p-3 bg-green-50 border border-green-200 rounded-md">
					<p class="text-xs text-green-800">{successMessage}</p>
				</div>
			{/if}

			<!-- Content -->
			<div class="flex-1 overflow-y-auto px-6 py-4 pb-20 md:pb-4">
				{#if loading}
					<div class="text-center py-12 text-gray-500 text-sm">Loading...</div>
				{:else if filteredNotifications.length === 0}
					<div class="text-center py-12">
						<svg class="w-12 h-12 text-gray-300 mx-auto mb-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
							<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9"/>
						</svg>
						<h3 class="text-base font-semibold text-gray-900 mb-1">No notifications</h3>
						<p class="text-sm text-gray-500">You're all caught up!</p>
					</div>
				{:else}
					<div class="space-y-2">
						{#each filteredNotifications as notification (notification.id)}
							{@const isRead = notification.is_read}
							{@const friendRequest = getFriendRequestInfo(notification)}

							<div class="bg-white border border-gray-200 rounded-lg p-3 hover:bg-gray-50 transition-colors {!isRead ? 'border-blue-200 bg-blue-50/30' : ''}">
								{#if notification.type === 'friend_request' && friendRequest}
									<!-- Friend Request Notification -->
									<div class="flex items-center gap-3">
										<div class="w-11 h-11 rounded-full bg-gradient-to-br from-green-400 to-emerald-400 flex items-center justify-center text-white font-medium text-sm flex-shrink-0">
											{friendRequest.username.substring(0, 2).toUpperCase()}
										</div>
										<div class="flex-1 min-w-0">
											<h3 class="font-semibold text-gray-900 text-sm">{friendRequest.username}</h3>
											<p class="text-xs text-gray-500">Sent you a friend request</p>
											<p class="text-xs text-gray-400 mt-1">{formatDate(notification.created_at)}</p>
										</div>
										<div class="flex gap-2 flex-shrink-0">
											<button on:click={() => respondToFriendRequest(friendRequest.friendshipId, 'accept')} class="px-4 py-1.5 bg-green-500 text-white text-xs font-medium rounded-md hover:bg-green-600 transition-colors">Accept</button>
											<button on:click={() => respondToFriendRequest(friendRequest.friendshipId, 'reject')} class="px-4 py-1.5 bg-gray-100 text-gray-700 text-xs font-medium rounded-md hover:bg-gray-200 transition-colors">Decline</button>
										</div>
									</div>
								{:else}
									<!-- Generic Notification -->
									<div class="flex items-start gap-3">
										<div class="w-11 h-11 rounded-full bg-gradient-to-br from-blue-400 to-indigo-400 flex items-center justify-center text-white flex-shrink-0">
											<svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
												<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9"/>
											</svg>
										</div>
										<div class="flex-1 min-w-0">
											<p class="text-sm text-gray-900">{notification.message}</p>
											<p class="text-xs text-gray-400 mt-1">{formatDate(notification.created_at)}</p>
										</div>
									</div>
								{/if}
							</div>
						{/each}
					</div>
				{/if}
			</div>
		</div>
	</div>
{/if}

<style>
	div::-webkit-scrollbar { width: 8px; }
	div::-webkit-scrollbar-track { background: transparent; }
	div::-webkit-scrollbar-thumb { background: #cbd5e0; border-radius: 4px; }
	div::-webkit-scrollbar-thumb:hover { background: #a0aec0; }
</style>

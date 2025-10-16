<script lang="ts">
	import { onMount } from 'svelte';
	import { friendsWindowOpen } from '$lib/stores/friendsStore';

	interface Friend {
		id: number;
		username: string;
		is_online: boolean;
		last_seen: string | null;
	}

	interface FriendRequest {
		id: number;
		username: string;
		friendship_id: number;
		created_at: string;
	}

	interface SearchResult {
		id: number;
		username: string;
		status: string;
	}

	let activeTab = 'friends';
	let friends: Friend[] = [];
	let receivedRequests: FriendRequest[] = [];
	let sentRequests: FriendRequest[] = [];
	let searchResults: SearchResult[] = [];
	let searchQuery = '';
	let loading = false;
	let error = '';
	let successMessage = '';

	async function fetchFriends() {
		try {
			loading = true;
			const response = await fetch('http://localhost:5000/api/friends', {
				credentials: 'include'
			});
			if (!response.ok) throw new Error('Failed to fetch friends');
			friends = await response.json();
			loading = false;
		} catch (err) {
			error = err instanceof Error ? err.message : 'An error occurred';
			loading = false;
		}
	}

	async function fetchReceivedRequests() {
		try {
			loading = true;
			const response = await fetch('http://localhost:5000/api/friend_requests', {
				credentials: 'include'
			});
			if (!response.ok) throw new Error('Failed to fetch friend requests');
			receivedRequests = await response.json();
			loading = false;
		} catch (err) {
			error = err instanceof Error ? err.message : 'An error occurred';
			loading = false;
		}
	}

	async function fetchSentRequests() {
		try {
			loading = true;
			const response = await fetch('http://localhost:5000/api/sent_requests', {
				credentials: 'include'
			});
			if (!response.ok) throw new Error('Failed to fetch sent requests');
			sentRequests = await response.json();
			loading = false;
		} catch (err) {
			error = err instanceof Error ? err.message : 'An error occurred';
			loading = false;
		}
	}

	async function searchUsers() {
		if (searchQuery.length < 2) {
			searchResults = [];
			return;
		}
		try {
			const response = await fetch(`http://localhost:5000/search_users?q=${encodeURIComponent(searchQuery)}`, {
				credentials: 'include'
			});
			if (!response.ok) throw new Error('Failed to search users');
			searchResults = await response.json();
		} catch (err) {
			error = err instanceof Error ? err.message : 'An error occurred';
		}
	}

	async function sendFriendRequest(userId: number) {
		try {
			const response = await fetch('http://localhost:5000/send_friend_request', {
				method: 'POST',
				credentials: 'include',
				headers: { 'Content-Type': 'application/json' },
				body: JSON.stringify({ user_id: userId })
			});
			const data = await response.json();
			if (data.success) {
				successMessage = data.message;
				setTimeout(() => successMessage = '', 3000);
				await searchUsers();
				await fetchSentRequests();
			} else {
				error = data.message;
			}
		} catch (err) {
			error = err instanceof Error ? err.message : 'An error occurred';
		}
	}

	async function respondToRequest(friendshipId: number, response: string) {
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
				await fetchReceivedRequests();
				if (response === 'accept') await fetchFriends();
			} else {
				error = data.message;
			}
		} catch (err) {
			error = err instanceof Error ? err.message : 'An error occurred';
		}
	}

	async function cancelFriendRequest(friendshipId: number) {
		try {
			const response = await fetch('http://localhost:5000/cancel_friend_request', {
				method: 'POST',
				credentials: 'include',
				headers: { 'Content-Type': 'application/json' },
				body: JSON.stringify({ friendship_id: friendshipId })
			});
			const data = await response.json();
			if (data.success) {
				successMessage = data.message;
				setTimeout(() => successMessage = '', 3000);
				await fetchSentRequests();
			} else {
				error = data.message;
			}
		} catch (err) {
			error = err instanceof Error ? err.message : 'An error occurred';
		}
	}

	async function removeFriend(friendId: number) {
		if (!confirm('Are you sure you want to remove this friend?')) return;
		try {
			const response = await fetch('http://localhost:5000/remove_friend', {
				method: 'POST',
				credentials: 'include',
				headers: { 'Content-Type': 'application/json' },
				body: JSON.stringify({ friend_user_id: friendId })
			});
			const data = await response.json();
			if (data.success) {
				successMessage = data.message;
				setTimeout(() => successMessage = '', 3000);
				await fetchFriends();
			} else {
				error = data.message;
			}
		} catch (err) {
			error = err instanceof Error ? err.message : 'An error occurred';
		}
	}

	function getStatusBadge(status: string) {
		switch (status) {
			case 'friends':
				return { text: 'Friends', color: 'bg-green-100 text-green-800' };
			case 'request_sent':
				return { text: 'Request Sent', color: 'bg-yellow-100 text-yellow-800' };
			case 'request_received':
				return { text: 'Pending', color: 'bg-blue-100 text-blue-800' };
			default:
				return null;
		}
	}

	function formatDate(dateString: string) {
		const date = new Date(dateString);
		const now = new Date();
		const diff = now.getTime() - date.getTime();
		const days = Math.floor(diff / (1000 * 60 * 60 * 24));
		if (days === 0) return 'Today';
		if (days === 1) return 'Yesterday';
		if (days < 7) return `${days} days ago`;
		return date.toLocaleDateString();
	}

	function switchTab(tab: string) {
		activeTab = tab;
		error = '';
		successMessage = '';
		// Clear and disable search when not on Friends tab
		if (tab !== 'friends') {
			searchQuery = '';
		}
		if (tab === 'friends' && friends.length === 0) fetchFriends();
		else if (tab === 'requests' && receivedRequests.length === 0) fetchReceivedRequests();
		else if (tab === 'sent' && sentRequests.length === 0) fetchSentRequests();
	}

	$: if (searchQuery.length >= 2) {
		searchUsers();
	} else {
		searchResults = [];
	}

	$: if ($friendsWindowOpen) {
		fetchFriends();
		fetchReceivedRequests();
		fetchSentRequests();
	}
</script>

{#if $friendsWindowOpen}
	<div class="fixed inset-0 backdrop-blur-sm bg-black/30 z-50 flex items-center justify-center md:p-4" on:click={() => friendsWindowOpen.set(false)}>
		<div class="bg-white md:rounded-lg shadow-xl w-full h-full md:w-[600px] md:h-[700px] md:max-h-[90vh] flex flex-col" on:click|stopPropagation>
			<div class="px-6 py-4 border-b border-gray-200 flex items-center justify-between">
				<h1 class="text-xl font-semibold text-gray-900">Friends</h1>
				<button on:click={() => friendsWindowOpen.set(false)} class="text-gray-400 hover:text-gray-600">
					<svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
						<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/>
					</svg>
				</button>
			</div>

			<div class="px-6 py-4 border-b border-gray-200">
				<div class="relative">
					<input type="text" bind:value={searchQuery} placeholder="Search for users..." disabled={activeTab !== 'friends'} class="w-full px-4 py-2 bg-gray-50 rounded-md text-sm text-gray-700 placeholder-gray-400 focus:outline-none focus:ring-1 focus:ring-gray-300 focus:bg-white transition-all pr-10 disabled:opacity-50 disabled:cursor-not-allowed"/>
					<svg class="absolute right-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
						<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"/>
					</svg>
				</div>

				<div class="flex gap-4 mt-4">
					<button on:click={() => switchTab('friends')} class="pb-2 px-1 text-sm font-medium transition-colors {activeTab === 'friends' ? 'text-gray-900 border-b-2 border-gray-900' : 'text-gray-500 hover:text-gray-700'}">
						Friends {friends.length > 0 ? `(${friends.length})` : ''}
					</button>
					<button on:click={() => switchTab('requests')} class="pb-2 px-1 text-sm font-medium transition-colors {activeTab === 'requests' ? 'text-gray-900 border-b-2 border-gray-900' : 'text-gray-500 hover:text-gray-700'}">
						Requests {receivedRequests.length > 0 ? `(${receivedRequests.length})` : ''}
					</button>
					<button on:click={() => switchTab('sent')} class="pb-2 px-1 text-sm font-medium transition-colors {activeTab === 'sent' ? 'text-gray-900 border-b-2 border-gray-900' : 'text-gray-500 hover:text-gray-700'}">
						Sent {sentRequests.length > 0 ? `(${sentRequests.length})` : ''}
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

			<div class="flex-1 overflow-y-auto px-6 py-4 pb-20 md:pb-4">
				{#if searchQuery.length >= 2}
					<div class="mb-6">
						<h2 class="text-xs font-semibold text-gray-500 uppercase tracking-wider mb-3">Search Results</h2>
						{#if searchResults.length === 0}
							<div class="text-center py-8 text-gray-500 text-sm">No users found</div>
						{:else}
							<div class="space-y-2">
								{#each searchResults as user (user.id)}
									<div class="bg-white border border-gray-200 rounded-lg p-3 hover:bg-gray-50 transition-colors">
										<div class="flex items-center gap-3">
											<div class="w-11 h-11 rounded-full bg-gradient-to-br from-purple-400 to-pink-400 flex items-center justify-center text-white font-medium text-sm flex-shrink-0">
												{user.username.substring(0, 2).toUpperCase()}
											</div>
											<div class="flex-1 min-w-0">
												<h3 class="font-semibold text-gray-900 truncate text-sm">{user.username}</h3>
											</div>
											<div class="flex-shrink-0">
												{#if user.status === 'none'}
													<button on:click={() => sendFriendRequest(user.id)} class="px-4 py-1.5 bg-blue-500 text-white text-xs font-medium rounded-md hover:bg-blue-600 transition-colors">Add Friend</button>
												{:else}
													{@const badge = getStatusBadge(user.status)}
													{#if badge}
														<div class="px-3 py-1.5 {badge.color} text-xs font-medium rounded-md">{badge.text}</div>
													{/if}
												{/if}
											</div>
										</div>
									</div>
								{/each}
							</div>
						{/if}
					</div>
				{:else if activeTab === 'friends'}
					{#if loading}
						<div class="text-center py-12 text-gray-500 text-sm">Loading...</div>
					{:else if friends.length === 0}
						<div class="text-center py-12">
							<svg class="w-12 h-12 text-gray-300 mx-auto mb-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
								<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z"/>
							</svg>
							<h3 class="text-base font-semibold text-gray-900 mb-1">No friends yet</h3>
							<p class="text-sm text-gray-500">Search for users above to add friends</p>
						</div>
					{:else}
						<div class="space-y-2">
							{#each friends as friend (friend.id)}
								<div class="bg-white border border-gray-200 rounded-lg p-3 hover:bg-gray-50 transition-colors">
									<div class="flex items-center gap-3">
										<div class="relative flex-shrink-0">
											<div class="w-11 h-11 rounded-full bg-gradient-to-br from-blue-400 to-indigo-400 flex items-center justify-center text-white font-medium text-sm">
												{friend.username.substring(0, 2).toUpperCase()}
											</div>
											{#if friend.is_online}
												<div class="absolute bottom-0 right-0 w-3 h-3 bg-green-500 border-2 border-white rounded-full"></div>
											{/if}
										</div>
										<div class="flex-1 min-w-0">
											<h3 class="font-semibold text-gray-900 truncate text-sm">{friend.username}</h3>
											<p class="text-xs text-gray-500">{friend.is_online ? 'Online' : friend.last_seen ? `Last seen ${formatDate(friend.last_seen)}` : 'Offline'}</p>
										</div>
										<div class="flex items-center gap-2 flex-shrink-0">
											<a href="/messenger?user={friend.id}" class="px-4 py-1.5 bg-blue-500 text-white text-xs font-medium rounded-md hover:bg-blue-600 transition-colors">Message</a>
											<button on:click={() => removeFriend(friend.id)} class="p-1.5 text-gray-400 hover:text-gray-600 hover:bg-gray-100 rounded-md transition-colors" title="Remove Friend">
												<svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
													<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/>
												</svg>
											</button>
										</div>
									</div>
								</div>
							{/each}
						</div>
					{/if}
				{:else if activeTab === 'requests'}
					{#if loading}
						<div class="text-center py-12 text-gray-500 text-sm">Loading...</div>
					{:else if receivedRequests.length === 0}
						<div class="text-center py-12">
							<svg class="w-12 h-12 text-gray-300 mx-auto mb-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
								<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M20 13V6a2 2 0 00-2-2H6a2 2 0 00-2 2v7m16 0v5a2 2 0 01-2 2H6a2 2 0 01-2-2v-5m16 0h-2.586a1 1 0 00-.707.293l-2.414 2.414a1 1 0 01-.707.293h-3.172a1 1 0 01-.707-.293l-2.414-2.414A1 1 0 006.586 13H4"/>
							</svg>
							<h3 class="text-base font-semibold text-gray-900 mb-1">No pending requests</h3>
							<p class="text-sm text-gray-500">Friend requests will appear here</p>
						</div>
					{:else}
						<div class="space-y-2">
							{#each receivedRequests as request (request.friendship_id)}
								<div class="bg-white border border-gray-200 rounded-lg p-3 hover:bg-gray-50 transition-colors">
									<div class="flex items-center gap-3">
										<div class="w-11 h-11 rounded-full bg-gradient-to-br from-green-400 to-emerald-400 flex items-center justify-center text-white font-medium text-sm flex-shrink-0">
											{request.username.substring(0, 2).toUpperCase()}
										</div>
										<div class="flex-1 min-w-0">
											<h3 class="font-semibold text-gray-900 text-sm">{request.username}</h3>
											<p class="text-xs text-gray-500">{formatDate(request.created_at)}</p>
										</div>
										<div class="flex gap-2 flex-shrink-0">
											<button on:click={() => respondToRequest(request.friendship_id, 'accept')} class="px-4 py-1.5 bg-green-500 text-white text-xs font-medium rounded-md hover:bg-green-600 transition-colors">Accept</button>
											<button on:click={() => respondToRequest(request.friendship_id, 'reject')} class="px-4 py-1.5 bg-gray-100 text-gray-700 text-xs font-medium rounded-md hover:bg-gray-200 transition-colors">Decline</button>
										</div>
									</div>
								</div>
							{/each}
						</div>
					{/if}
				{:else if activeTab === 'sent'}
					{#if loading}
						<div class="text-center py-12 text-gray-500 text-sm">Loading...</div>
					{:else if sentRequests.length === 0}
						<div class="text-center py-12">
							<svg class="w-12 h-12 text-gray-300 mx-auto mb-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
								<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8"/>
							</svg>
							<h3 class="text-base font-semibold text-gray-900 mb-1">No sent requests</h3>
							<p class="text-sm text-gray-500">Friend requests you send will appear here</p>
						</div>
					{:else}
						<div class="space-y-2">
							{#each sentRequests as request (request.friendship_id)}
								<div class="bg-white border border-gray-200 rounded-lg p-3 hover:bg-gray-50 transition-colors">
									<div class="flex items-center gap-3">
										<div class="w-11 h-11 rounded-full bg-gradient-to-br from-yellow-400 to-orange-400 flex items-center justify-center text-white font-medium text-sm flex-shrink-0">
											{request.username.substring(0, 2).toUpperCase()}
										</div>
										<div class="flex-1 min-w-0">
											<h3 class="font-semibold text-gray-900 text-sm">{request.username}</h3>
											<p class="text-xs text-gray-500">Sent {formatDate(request.created_at)}</p>
										</div>
										<button on:click={() => cancelFriendRequest(request.friendship_id)} class="px-4 py-1.5 bg-gray-100 text-gray-700 text-xs font-medium rounded-md hover:bg-gray-200 transition-colors flex-shrink-0">Cancel</button>
									</div>
								</div>
							{/each}
						</div>
					{/if}
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

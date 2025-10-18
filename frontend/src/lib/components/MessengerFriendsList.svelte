<script lang="ts">
	import { onMount, onDestroy, createEventDispatcher } from 'svelte';
	import { getSocket } from '$lib/socket';
	import { hasUnreadMessages } from '$lib/stores/messengerStore';
	import { friendsRefresh } from '$lib/stores/friendsStore';
	import type { Socket } from 'socket.io-client';

	const dispatch = createEventDispatcher();

	interface Contact {
		id: number;
		name: string;
		avatar: string;
		lastMessage: string;
		timestamp: string;
		isPinned: boolean;
		isOnline: boolean;
		unreadCount?: number;
		isVoiceMessage?: boolean;
		avatarColor?: string;
		messenger_id?: number;
	}

	export let selectedContactId: number | null = null;

	let contacts: Contact[] = [];
	let searchQuery = "";
	let loading = true;
	let error = "";
	let socket: Socket;

	$: pinnedContacts = contacts.filter(c => c.isPinned);
	$: allContacts = contacts.filter(c => !c.isPinned);

	$: filteredPinned = pinnedContacts.filter(c =>
		c.name.toLowerCase().includes(searchQuery.toLowerCase())
	);

	$: filteredAll = allContacts.filter(c =>
		c.name.toLowerCase().includes(searchQuery.toLowerCase())
	);

	// Update hasUnreadMessages store whenever contacts change
	$: {
		const hasUnread = contacts.some(c => (c.unreadCount || 0) > 0);
		hasUnreadMessages.set(hasUnread);
	}

	function selectContact(contactId: number) {
		selectedContactId = contactId;

		// Clear unread count for selected contact
		const contact = contacts.find(c => c.id === contactId);
		if (contact) {
			contact.unreadCount = 0;
			// Trigger reactive update
			contacts = contacts;
		}

		dispatch('selectContact', contactId);
	}

	async function fetchFriendsList() {
		try {
			loading = true;
			const response = await fetch('http://localhost:5000/api/friend_list', {
				credentials: 'include'
			});

			if (!response.ok) {
				throw new Error('Failed to fetch friends list');
			}

			const data = await response.json();

			// Transform backend data to Contact format
			contacts = data.map((friend: any) => ({
				id: friend.id,
				name: friend.username,
				avatar: friend.avatar || '',
				lastMessage: friend.last_message,
				timestamp: friend.timestamp,
				isPinned: false, // You can implement pinning logic later
				isOnline: friend.is_online,
				avatarColor: "from-blue-400 to-indigo-400",
				messenger_id: friend.messenger_id,
				unreadCount: friend.unread_count || 0
			}));

			loading = false;
		} catch (err) {
			error = err instanceof Error ? err.message : 'An error occurred';
			loading = false;
			console.error('Error fetching friends list:', err);
		}
	}

	function handleNewMessage(messageData: any) {
		const senderId = messageData.sender_id;
		const content = messageData.content;
		const timestamp = messageData.created_at;

		// Find the contact in the list
		const contactIndex = contacts.findIndex(c => c.id === senderId);
		if (contactIndex !== -1) {
			const contact = contacts[contactIndex];

			// Update contact's last message and timestamp
			contact.lastMessage = content;
			contact.timestamp = timestamp;

			// Increment unread count if message is not from selected contact
			if (selectedContactId !== senderId) {
				contact.unreadCount = (contact.unreadCount || 0) + 1;
			}

			// Remove contact from current position
			contacts.splice(contactIndex, 1);

			// Add to the beginning of the list (newest on top)
			contacts = [contact, ...contacts];
		}
	}

	onMount(() => {
		fetchFriendsList();

		// Get shared Socket.IO connection
		socket = getSocket();

		const handleMessagesReadInList = (data: any) => {
			const contact = contacts.find(c => c.id === data.friend_id);
			if (contact) {
				contact.unreadCount = 0;
				contacts = contacts;
			}
		};

		const handleFriendListUpdated = (data: any) => {
			console.log('[MessengerFriendsList] Friend list updated:', data);
			// Refresh the friend list when a friend is added or removed
			fetchFriendsList();
		};

		const handleUserStatusChanged = (data: any) => {
			console.log('[MessengerFriendsList] User status changed:', data);
			// Update the online status of the user in the contacts list
			const contact = contacts.find(c => c.id === data.user_id);
			if (contact) {
				contact.isOnline = data.is_online;
				contacts = contacts; // Trigger reactivity
			}
		};

		// Listen for new messages
		socket.on('new_message', handleNewMessage);

		// Listen for messages marked as read
		socket.on('messages_read', handleMessagesReadInList);

		// Listen for friend list updates
		socket.on('friend_list_updated', handleFriendListUpdated);

		// Listen for user status changes
		socket.on('user_status_changed', handleUserStatusChanged);

		// Subscribe to friends refresh store
		const unsubscribe = friendsRefresh.subscribe((state) => {
			console.log('[MessengerFriendsList] friendsRefresh update:', state);
			if (state.shouldRefresh) {
				console.log('[MessengerFriendsList] Refreshing friends list...');
				fetchFriendsList();
				friendsRefresh.reset();
			}
		});

		// Cleanup function to remove event listeners
		return () => {
			socket.off('new_message', handleNewMessage);
			socket.off('messages_read', handleMessagesReadInList);
			socket.off('friend_list_updated', handleFriendListUpdated);
			socket.off('user_status_changed', handleUserStatusChanged);
			unsubscribe();
		};
	});

	onDestroy(() => {
		// Don't disconnect the shared socket, just clean up listeners
		// The socket will be managed by the socket.ts module
	});
</script>

<div class="w-full md:w-80 bg-white h-screen flex flex-col border-r border-gray-200">
	<!-- Header -->
	<div class="px-5 py-4 border-b border-gray-200">
		<div class="flex items-center justify-between mb-3.5">
			<h1 class="text-xs font-semibold text-gray-500 uppercase tracking-wider">
				ALL CHATS
			</h1>
		</div>

		<!-- Search Bar -->
		<div class="relative">
			<input
				type="text"
				bind:value={searchQuery}
				placeholder="Search"
				class="w-full px-3.5 py-2 bg-gray-50 rounded-md text-sm text-gray-700 placeholder-gray-400 focus:outline-none focus:ring-1 focus:ring-gray-300 focus:bg-white transition-all pr-9"
			/>
			<svg
				class="absolute right-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400"
				fill="none"
				stroke="currentColor"
				viewBox="0 0 24 24"
			>
				<path
					stroke-linecap="round"
					stroke-linejoin="round"
					stroke-width="2"
					d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"
				/>
			</svg>
		</div>
	</div>

	<!-- Contacts List -->
	<div class="flex-1 overflow-y-auto bg-white">
		{#if loading}
			<div class="flex items-center justify-center py-8">
				<div class="text-gray-500 text-sm">Loading...</div>
			</div>
		{:else if error}
			<div class="flex items-center justify-center py-8">
				<div class="text-red-500 text-sm">{error}</div>
			</div>
		{:else}
		<!-- Pinned Section -->
		{#if filteredPinned.length > 0}
			<div class="px-4 py-3">
				<h2 class="text-[10px] font-bold text-gray-400 uppercase tracking-wider mb-2.5 px-2">
					PINNED
				</h2>
				<div class="space-y-0.5">
					{#each filteredPinned as contact (contact.id)}
						<button
							on:click={() => selectContact(contact.id)}
							class="w-full flex items-center gap-3 px-3 py-2.5 rounded-lg hover:bg-gray-50 transition-colors duration-150 {selectedContactId === contact.id ? 'bg-gray-100' : ''}"
						>
							<!-- Avatar with online status -->
							<div class="relative flex-shrink-0">
								<div class="w-11 h-11 rounded-full bg-gradient-to-br {contact.avatarColor || 'from-purple-400 to-pink-400'} flex items-center justify-center text-white font-medium text-sm">
									{contact.name.split(' ').map(n => n[0]).join('')}
								</div>
								{#if contact.isOnline}
									<div class="absolute bottom-0 right-0 w-3 h-3 bg-green-500 border-2 border-white rounded-full"></div>
								{/if}
							</div>

							<!-- Contact Info -->
							<div class="flex-1 min-w-0 text-left">
								<div class="flex items-center justify-between mb-0.5">
									<h3 class="font-semibold text-gray-900 text-[13px] truncate">
										{contact.name}
									</h3>
									<div class="flex items-center gap-1.5 ml-2 flex-shrink-0">
										<span class="text-[11px] text-gray-400">
											{contact.timestamp}
										</span>
										{#if contact.unreadCount > 0}
											<span class="bg-blue-500 text-white text-[10px] font-bold rounded-full px-1.5 py-0.5 min-w-[18px] text-center">
												{contact.unreadCount}
											</span>
										{/if}
									</div>
								</div>
								<p class="text-[13px] truncate leading-tight" class:text-gray-900={contact.unreadCount > 0} class:font-semibold={contact.unreadCount > 0} class:text-gray-500={contact.unreadCount === 0}>
									{contact.lastMessage}
								</p>
							</div>
						</button>
					{/each}
				</div>
			</div>
		{/if}

		<!-- All Messages Section -->
		{#if filteredAll.length > 0}
			<div class="px-4 py-3">
				<h2 class="text-[10px] font-bold text-gray-400 uppercase tracking-wider mb-2.5 px-2">
					ALL MESSAGES
				</h2>
				<div class="space-y-0.5">
					{#each filteredAll as contact (contact.id)}
						<button
							on:click={() => selectContact(contact.id)}
							class="w-full flex items-center gap-3 px-3 py-2.5 rounded-lg hover:bg-gray-50 transition-colors duration-150 {selectedContactId === contact.id ? 'bg-gray-100' : ''}"
						>
							<!-- Avatar with online status -->
							<div class="relative flex-shrink-0">
								<div class="w-11 h-11 rounded-full bg-gradient-to-br {contact.avatarColor || 'from-blue-400 to-indigo-400'} flex items-center justify-center text-white font-medium text-sm">
									{contact.name.split(' ').map(n => n[0]).join('')}
								</div>
								{#if contact.isOnline}
									<div class="absolute bottom-0 right-0 w-3 h-3 bg-green-500 border-2 border-white rounded-full"></div>
								{/if}
							</div>

							<!-- Contact Info -->
							<div class="flex-1 min-w-0 text-left">
								<div class="flex items-center justify-between mb-0.5">
									<h3 class="font-semibold text-gray-900 text-[13px] truncate">
										{contact.name}
									</h3>
									<div class="flex items-center gap-1.5 ml-2 flex-shrink-0">
										<span class="text-[11px] text-gray-400">
											{contact.timestamp}
										</span>
										{#if contact.unreadCount > 0}
											<span class="bg-blue-500 text-white text-[10px] font-bold rounded-full px-1.5 py-0.5 min-w-[18px] text-center">
												{contact.unreadCount}
											</span>
										{/if}
									</div>
								</div>
								<div class="flex items-center gap-1.5">
									{#if contact.isVoiceMessage}
										<svg class="w-3 h-3 text-gray-400 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
											<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 11a7 7 0 01-7 7m0 0a7 7 0 01-7-7m7 7v4m0 0H8m4 0h4m-4-8a3 3 0 01-3-3V5a3 3 0 116 0v6a3 3 0 01-3 3z"/>
										</svg>
									{/if}
									<p class="text-[13px] truncate leading-tight" class:text-gray-900={contact.unreadCount > 0} class:font-semibold={contact.unreadCount > 0} class:text-gray-500={contact.unreadCount === 0}>
										{contact.lastMessage}
									</p>
								</div>
							</div>
						</button>
					{/each}
				</div>
			</div>
		{/if}

		{#if filteredPinned.length === 0 && filteredAll.length === 0}
			<div class="px-6 py-8 text-center">
				<p class="text-gray-500 text-sm">No contacts found</p>
			</div>
		{/if}
		{/if}
	</div>
</div>

<style>
	/* Custom scrollbar */
	div::-webkit-scrollbar {
		width: 6px;
	}

	div::-webkit-scrollbar-track {
		background: transparent;
	}

	div::-webkit-scrollbar-thumb {
		background: #cbd5e0;
		border-radius: 3px;
	}

	div::-webkit-scrollbar-thumb:hover {
		background: #a0aec0;
	}
</style>

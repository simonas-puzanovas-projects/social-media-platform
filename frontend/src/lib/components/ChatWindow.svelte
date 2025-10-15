<script lang="ts">
	import { onMount, onDestroy } from 'svelte';
	import { io } from 'socket.io-client';

	export let selectedFriendId: number | null = null;

	interface Message {
		id: number;
		sender_id: number;
		sender: string;
		content: string;
		is_read: boolean;
		created_at: string;
	}

	interface Friend {
		id: number;
		username: string;
		is_online: boolean;
	}

	let messages: Message[] = [];
	let friend: Friend | null = null;
	let messengerId: number | null = null;
	let newMessage = "";
	let loading = false;
	let error = "";
	let messagesContainer: HTMLDivElement;
	let socket: any = null;
	let currentUserId: number | null = null;

	$: if (selectedFriendId) {
		loadMessages(selectedFriendId);
	}

	async function loadMessages(friendId: number) {
		try {
			loading = true;
			error = "";
			const response = await fetch(`http://localhost:5000/api/messages/${friendId}`, {
				credentials: 'include'
			});

			if (!response.ok) {
				throw new Error('Failed to fetch messages');
			}

			const data = await response.json();
			messages = data.messages;
			friend = data.friend;
			messengerId = data.messenger_id;
			loading = false;

			// Mark messages as read
			if (socket && friendId) {
				socket.emit('mark_read', { friend_id: friendId });
			}

			// Scroll to bottom after messages load
			setTimeout(scrollToBottom, 100);
		} catch (err) {
			error = err instanceof Error ? err.message : 'An error occurred';
			loading = false;
			console.error('Error fetching messages:', err);
		}
	}

	async function sendMessage() {
		if (!newMessage.trim() || !selectedFriendId) return;

		try {
			const response = await fetch('http://localhost:5000/api/send_message', {
				method: 'POST',
				headers: {
					'Content-Type': 'application/json',
				},
				credentials: 'include',
				body: JSON.stringify({
					friend_id: selectedFriendId,
					content: newMessage.trim()
				})
			});

			if (!response.ok) {
				throw new Error('Failed to send message');
			}

			const data = await response.json();
			// Message will be added via socket event
			newMessage = "";
		} catch (err) {
			console.error('Error sending message:', err);
			error = err instanceof Error ? err.message : 'Failed to send message';
		}
	}

	function scrollToBottom() {
		if (messagesContainer) {
			messagesContainer.scrollTop = messagesContainer.scrollHeight;
		}
	}

	function handleKeydown(e: KeyboardEvent) {
		if (e.key === 'Enter' && !e.shiftKey) {
			e.preventDefault();
			sendMessage();
		}
	}

	async function getCurrentUserId() {
		try {
			const response = await fetch('http://localhost:5000/api/current_user', {
				credentials: 'include'
			});
			if (response.ok) {
				const data = await response.json();
				currentUserId = data.id;
			}
		} catch (err) {
			console.error('Error fetching current user:', err);
		}
	}

	onMount(() => {
		getCurrentUserId();

		// Initialize Socket.IO connection
		socket = io('http://localhost:5000', {
			withCredentials: true
		});

		socket.on('connect', () => {
			console.log('Connected to socket');
		});

		socket.on('new_message', (data: any) => {
			console.log('New message received:', data);
			if (data.chat_id === messengerId) {
				// Add the message to the list
				const messageExists = messages.some(msg => msg.id === data.id);
				if (!messageExists) {
					messages = [...messages, {
						id: data.id,
						sender_id: data.sender_id,
						sender: data.sender,
						content: data.content,
						is_read: data.is_read,
						created_at: data.created_at
					}];
					setTimeout(scrollToBottom, 50);

					// Mark as read if we're viewing this chat
					if (socket && selectedFriendId) {
						socket.emit('mark_read', { friend_id: selectedFriendId });
					}
				}
			}
		});

		socket.on('messages_read', (data: any) => {
			console.log('Messages read event received:', data);
			// Update is_read status for messages that were read
			const messageIds = data.message_ids || [];
			messages = messages.map(msg => {
				if (messageIds.includes(msg.id)) {
					return { ...msg, is_read: true };
				}
				return msg;
			});
		});
	});

	onDestroy(() => {
		if (socket) {
			socket.disconnect();
		}
	});
</script>

{#if selectedFriendId && friend}
	<div class="flex flex-col h-screen bg-white">
		<!-- Chat Header -->
		<div class="px-6 py-4 border-b border-gray-200 flex items-center justify-between bg-white">
			<div class="flex items-center gap-3">
				<div class="relative">
					<div class="w-10 h-10 rounded-full bg-gradient-to-br from-purple-400 to-pink-400 flex items-center justify-center text-white font-medium text-sm">
						{friend.username.split(' ').map(n => n[0]).join('')}
					</div>
					{#if friend.is_online}
						<div class="absolute bottom-0 right-0 w-3 h-3 bg-green-500 border-2 border-white rounded-full"></div>
					{/if}
				</div>
				<div>
					<h2 class="font-semibold text-gray-900">{friend.username}</h2>
					<p class="text-xs text-gray-500">{friend.is_online ? 'Online' : 'Offline'}</p>
				</div>
			</div>
			<div class="flex items-center gap-2">
				<button aria-label="Voice chat" class="p-2 hover:bg-gray-100 rounded-lg transition-colors">
					<svg class="w-5 h-5 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
						<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 5a2 2 0 012-2h3.28a1 1 0 01.948.684l1.498 4.493a1 1 0 01-.502 1.21l-2.257 1.13a11.042 11.042 0 005.516 5.516l1.13-2.257a1 1 0 011.21-.502l4.493 1.498a1 1 0 01.684.949V19a2 2 0 01-2 2h-1C9.716 21 3 14.284 3 6V5z"/>
					</svg>
				</button>
				<button aria-label="Video chat" class="p-2 hover:bg-gray-100 rounded-lg transition-colors">
					<svg class="w-5 h-5 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
						<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 10l4.553-2.276A1 1 0 0121 8.618v6.764a1 1 0 01-1.447.894L15 14M5 18h8a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v8a2 2 0 002 2z"/>
					</svg>
				</button>
			</div>
		</div>

		<!-- Messages Container -->
		<div
			bind:this={messagesContainer}
			class="flex-1 overflow-y-auto px-6 py-4 bg-gray-50"
		>
			{#if loading}
				<div class="flex items-center justify-center h-full">
					<div class="text-gray-500 text-sm">Loading messages...</div>
				</div>
			{:else if error}
				<div class="flex items-center justify-center h-full">
					<div class="text-red-500 text-sm">{error}</div>
				</div>
			{:else if messages.length === 0}
				<div class="flex items-center justify-center h-full">
					<div class="text-gray-500 text-sm">No messages yet. Start the conversation!</div>
				</div>
			{:else}
				<div class="space-y-4">
					{#each messages as message (message.id)}
						<div class="flex {message.sender_id === currentUserId ? 'justify-start' : 'justify-end'}">
							<div class="flex gap-2 max-w-[70%] {message.sender_id === currentUserId ? 'flex-row' : 'flex-row-reverse'}">
								<div class="w-8 h-8 rounded-full bg-gradient-to-br from-blue-400 to-indigo-400 flex items-center justify-center text-white font-medium text-xs flex-shrink-0">
									{message.sender[0].toUpperCase()}
								</div>
								<div class="flex flex-col {message.sender_id === currentUserId ? 'items-start' : 'items-end'}">
									<div class="px-4 py-2 rounded-2xl {message.sender_id === currentUserId ? 'bg-blue-500 text-white' : 'bg-white text-gray-900 border border-gray-200'}">
										<p class="text-sm break-words">{message.content}</p>
									</div>
									<div class="flex items-center gap-1 mt-1 px-1">
										<span class="text-xs text-gray-400">{message.created_at}</span>
										{#if message.sender_id === currentUserId && message.is_read}
											<svg class="w-3 h-3 text-blue-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
												<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"/>
											</svg>
										{/if}
									</div>
								</div>
							</div>
						</div>
					{/each}
				</div>
			{/if}
		</div>

		<!-- Message Input -->
		<div class="px-6 py-4 bg-white border-t border-gray-200">
			<div class="flex items-end gap-3">
				<button aria-label="Add attachment" class="p-2 text-gray-500 hover:text-gray-700 transition-colors">
					<svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
						<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4"/>
					</svg>
				</button>
				<div class="flex-1 relative">
					<input
						type="text"
						bind:value={newMessage}
						on:keydown={handleKeydown}
						placeholder="Type a message..."
						class="w-full px-4 py-3 bg-gray-100 rounded-full text-sm text-gray-700 placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:bg-white transition-all"
					/>
				</div>
				<button
					aria-label="Send message"
					on:click={sendMessage}
					disabled={!newMessage.trim()}
					class="p-3 bg-blue-500 text-white rounded-full hover:bg-blue-600 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
				>
					<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
						<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8"/>
					</svg>
				</button>
			</div>
		</div>
	</div>
{:else}
	<div class="flex items-center justify-center h-screen bg-gray-50">
		<div class="text-center">
			<svg class="w-24 h-24 mx-auto text-gray-300 mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
				<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z"/>
			</svg>
			<h3 class="text-lg font-semibold text-gray-700 mb-2">Select a conversation</h3>
			<p class="text-sm text-gray-500">Choose a friend from the list to start messaging</p>
		</div>
	</div>
{/if}

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

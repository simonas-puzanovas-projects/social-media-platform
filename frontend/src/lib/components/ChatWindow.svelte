<script lang="ts">
	import { onMount, onDestroy } from 'svelte';
	import { fade, fly, scale } from 'svelte/transition';
	import { quintOut } from 'svelte/easing';
	import { getSocket } from '$lib/socket';
	import type { Socket } from 'socket.io-client';

	export let selectedFriendId: number | null = null;
	export let onBack: (() => void) | undefined = undefined;

	interface Message {
		id: number;
		sender_id: number;
		sender: string;
		sender_avatar?: string;
		sender_display_name?: string;
		content: string;
		image_url?: string;
		is_read: boolean;
		created_at: string;
	}

	interface Friend {
		id: number;
		username: string;
		avatar_path?: string;
		display_name?: string;
		is_online: boolean;
	}

	let messages: Message[] = [];
	let friend: Friend | null = null;
	let messengerId: number | null = null;
	let newMessage = "";
	let loading = false;
	let error = "";
	let messagesContainer: HTMLDivElement;
	let socket: Socket;
	let currentUserId: number | null = null;
	let selectedImage: File | null = null;
	let imagePreview: string | null = null;
	let uploading = false;
	let fileInput: HTMLInputElement;

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
		if ((!newMessage.trim() && !selectedImage) || !selectedFriendId) return;

		try {
			uploading = true;
			let imageUrl = null;

			// Upload image first if one is selected
			if (selectedImage) {
				const formData = new FormData();
				formData.append('image', selectedImage);

				const uploadResponse = await fetch('http://localhost:5000/api/upload_chat_image', {
					method: 'POST',
					credentials: 'include',
					body: formData
				});

				if (!uploadResponse.ok) {
					throw new Error('Failed to upload image');
				}

				const uploadData = await uploadResponse.json();
				imageUrl = uploadData.image_url;
			}

			// Send message with optional image URL
			const response = await fetch('http://localhost:5000/api/send_message', {
				method: 'POST',
				headers: {
					'Content-Type': 'application/json',
				},
				credentials: 'include',
				body: JSON.stringify({
					friend_id: selectedFriendId,
					content: newMessage.trim() || null,
					image_url: imageUrl
				})
			});

			if (!response.ok) {
				throw new Error('Failed to send message');
			}

			const data = await response.json();
			// Message will be added via socket event
			newMessage = "";
			clearImagePreview();
		} catch (err) {
			console.error('Error sending message:', err);
			error = err instanceof Error ? err.message : 'Failed to send message';
		} finally {
			uploading = false;
		}
	}

	function handleImageSelect(event: Event) {
		const target = event.target as HTMLInputElement;
		const file = target.files?.[0];

		if (file) {
			// Validate file type
			const allowedTypes = ['image/png', 'image/jpeg', 'image/jpg', 'image/gif', 'image/webp'];
			if (!allowedTypes.includes(file.type)) {
				error = 'Invalid file type. Only images allowed.';
				return;
			}

			// Validate file size (10MB max)
			if (file.size > 10 * 1024 * 1024) {
				error = 'File too large. Maximum size is 10MB.';
				return;
			}

			selectedImage = file;

			// Create preview
			const reader = new FileReader();
			reader.onload = (e) => {
				imagePreview = e.target?.result as string;
			};
			reader.readAsDataURL(file);
		}
	}

	function clearImagePreview() {
		selectedImage = null;
		imagePreview = null;
		if (fileInput) {
			fileInput.value = '';
		}
	}

	function openImagePicker() {
		fileInput?.click();
	}

	function scrollToBottom() {
		if (messagesContainer) {
			messagesContainer.scrollTo({
				top: messagesContainer.scrollHeight,
				behavior: 'smooth'
			});
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

		// Get shared Socket.IO connection
		socket = getSocket();

		const handleNewMessage = (data: any) => {
			console.log('New message received:', data);
			if (data.chat_id === messengerId) {
				// Add the message to the list
				const messageExists = messages.some(msg => msg.id === data.id);
				if (!messageExists) {
					messages = [...messages, {
						id: data.id,
						sender_id: data.sender_id,
						sender: data.sender,
						sender_avatar: data.sender_avatar,
						content: data.content,
						image_url: data.image_url,
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
		};

		const handleMessagesRead = (data: any) => {
			console.log('Messages read event received:', data);
			// Update is_read status for messages that were read
			const messageIds = data.message_ids || [];
			messages = messages.map(msg => {
				if (messageIds.includes(msg.id)) {
					return { ...msg, is_read: true };
				}
				return msg;
			});
		};

		socket.on('new_message', handleNewMessage);
		socket.on('messages_read', handleMessagesRead);

		// Cleanup function to remove event listeners
		return () => {
			socket.off('new_message', handleNewMessage);
			socket.off('messages_read', handleMessagesRead);
		};
	});

	onDestroy(() => {
		// Don't disconnect the shared socket, just clean up listeners
		// The socket will be managed by the socket.ts module
	});
</script>

{#if selectedFriendId && friend}
	<div class="flex flex-col h-screen bg-white max-w-4xl mx-auto shadow-soft-lg" in:fade="{{ duration: 400 }}">
		<!-- Chat Header -->
		<div class="px-4 md:px-6 py-4 border-b border-gray-200 flex items-center justify-between bg-white" in:fly="{{ x: 20, duration: 400, delay: 100 }}">
			<div class="flex items-center gap-3">
				<!-- Back button for mobile -->
				{#if onBack}
					<button
						on:click={onBack}
						class="md:hidden p-2 -ml-2 hover:bg-gray-100 rounded-lg transition-colors"
						aria-label="Back to conversations"
					>
						<svg class="w-5 h-5 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
							<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7"/>
						</svg>
					</button>
				{/if}
				<div class="relative">
					<div class="w-10 h-10 rounded-full bg-gradient-to-br from-purple-400 to-pink-400 flex items-center justify-center text-white font-medium text-sm overflow-hidden">
						{#if friend.avatar_path}
							<img src="http://localhost:5000/static/{friend.avatar_path}" alt={friend.username} class="w-full h-full object-cover" />
						{:else}
							{friend.username.split(' ').map(n => n[0]).join('')}
						{/if}
					</div>
					{#if friend.is_online}
						<div class="absolute bottom-0 right-0 w-3 h-3 bg-green-500 border-2 border-white rounded-full"></div>
					{/if}
				</div>
				<div>
					<h2 class="font-semibold text-gray-900">{friend.display_name || friend.username}</h2>
					<p class="text-xs text-gray-500">{friend.is_online ? 'Online' : 'Offline'}</p>
				</div>
			</div>
		</div>

		<!-- Messages Container -->
		<div
			bind:this={messagesContainer}
			class="flex-1 overflow-y-auto px-4 md:px-6 py-4 bg-gray-50"
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
						<div
							class="flex {message.sender_id === currentUserId ? 'justify-start' : 'justify-end'}"
							in:fly="{{ y: 20, duration: 300, easing: quintOut }}"
						>
							<div class="flex gap-2 max-w-[85%] md:max-w-[70%] {message.sender_id === currentUserId ? 'flex-row' : 'flex-row-reverse'}">
								<div class="w-8 h-8 rounded-full bg-gradient-to-br from-blue-400 to-indigo-400 flex items-center justify-center text-white font-medium text-xs flex-shrink-0 transition-transform duration-200 hover:scale-110 overflow-hidden">
									{#if message.sender_avatar}
										<img src="http://localhost:5000/static/{message.sender_avatar}" alt={message.sender} class="w-full h-full object-cover" />
									{:else}
										{message.sender[0].toUpperCase()}
									{/if}
								</div>
								<div class="flex flex-col {message.sender_id === currentUserId ? 'items-start' : 'items-end'}">
									<div class="rounded-2xl {message.sender_id === currentUserId ? 'bg-sage-500 text-white' : 'bg-white text-gray-900 border border-gray-100'} {message.image_url ? 'p-2' : 'px-4 py-2'} transition-all duration-200 hover:shadow-soft-md">
										{#if message.image_url}
											<img
												src={`http://localhost:5000/static/${message.image_url}`}
												alt="Shared image"
												class="max-w-xs max-h-64 rounded-lg cursor-pointer transition-transform duration-200 hover:scale-105"
												on:click={() => window.open(`http://localhost:5000/static/${message.image_url}`, '_blank')}
											/>
											{#if message.content}
												<p class="text-sm break-words mt-2 px-2">{message.content}</p>
											{/if}
										{:else}
											<p class="text-sm break-words">{message.content}</p>
										{/if}
									</div>
									<div class="flex items-center gap-1 mt-1 px-1">
										<span class="text-xs text-gray-400">{message.created_at}</span>
										{#if message.sender_id === currentUserId && message.is_read}
											<svg class="w-3 h-3 text-sage-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
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
		<div class="px-4 md:px-6 py-4 bg-white border-t border-gray-200">
			<!-- Image Preview -->
			{#if imagePreview}
				<div class="mb-3 relative inline-block" in:scale="{{ duration: 200, easing: quintOut }}">
					<img src={imagePreview} alt="Preview" class="max-h-32 rounded-lg border border-gray-200 shadow-md" />
					<button
						on:click={clearImagePreview}
						class="absolute -top-2 -right-2 w-6 h-6 bg-red-500 text-white rounded-full flex items-center justify-center hover:bg-red-600 hover:scale-110 transition-all duration-200"
						aria-label="Remove image"
					>
						<svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
							<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/>
						</svg>
					</button>
				</div>
			{/if}

			<div class="flex items-end gap-2 md:gap-3">
				<!-- Hidden file input -->
				<input
					type="file"
					bind:this={fileInput}
					on:change={handleImageSelect}
					accept="image/png,image/jpeg,image/jpg,image/gif,image/webp"
					class="hidden"
				/>

				<!-- Image upload button -->
				<button
					on:click={openImagePicker}
					aria-label="Add image"
					class="p-2 text-gray-500 hover:text-sage-500 hover:scale-110 transition-all duration-200"
					disabled={uploading}
				>
					<svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
						<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z"/>
					</svg>
				</button>

				<div class="flex-1 relative">
					<input
						type="text"
						bind:value={newMessage}
						on:keydown={handleKeydown}
						placeholder="Type a message..."
						disabled={uploading}
						class="w-full px-4 py-3 bg-gray-100 rounded-full text-sm text-gray-700 placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-sage-400 focus:bg-white transition-all disabled:opacity-50"
					/>
				</div>
				<button
					aria-label="Send message"
					on:click={sendMessage}
					disabled={(!newMessage.trim() && !selectedImage) || uploading}
					class="p-3 bg-sage-500 text-white rounded-full hover:bg-sage-600 hover:scale-110 active:scale-95 transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed disabled:hover:scale-100"
				>
					{#if uploading}
						<svg class="w-5 h-5 animate-spin" fill="none" viewBox="0 0 24 24">
							<circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
							<path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
						</svg>
					{:else}
						<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
							<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8"/>
						</svg>
					{/if}
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

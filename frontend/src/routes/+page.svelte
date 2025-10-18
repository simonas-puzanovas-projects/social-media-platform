<script lang="ts">
	import { onMount, onDestroy } from 'svelte';
	import Post from '$lib/components/Post.svelte';
	import { getSocket } from '$lib/socket';
	import { fetchUnreadMessageStatus } from '$lib/stores/messengerStore';
	import type { Socket } from 'socket.io-client';

	interface PageData {
		posts: Array<{
			id: number;
			owner_id: number;
			owner_name: string;
			image_path: string;
			created_at: string;
			likes: Array<{ user_id: number; username: string }>;
		}>;
		currentUserId: number;
		currentUsername: string;
	}

	let { data }: { data: PageData } = $props();
	let posts = $state(data.posts);
	let socket: Socket;

	function handlePostDeleted(event: any) {
		const postId = event.detail.postId;
		posts = posts.filter(p => p.id !== postId);
	}

	onMount(() => {
		document.addEventListener('postDeleted', handlePostDeleted);

		// Connect to socket for real-time updates
		socket = getSocket();

		// Fetch initial unread message status
		fetchUnreadMessageStatus();

		const handleNewPost = (postData: any) => {
			console.log('New post received:', postData);
			// Check if post already exists to avoid duplicates
			if (!posts.some(p => p.id === postData.post_id)) {
				// Prepend new post to the feed
				posts = [postData.post_data, ...posts];
			}
		};

		const handlePostDeletedSocket = (data: any) => {
			console.log('Post deleted via socket:', data);
			// Remove the deleted post from the feed
			posts = posts.filter(p => p.id !== data.post_id);
		};

		socket.on('new_post', handleNewPost);
		socket.on('post_deleted', handlePostDeletedSocket);

		return () => {
			socket.off('new_post', handleNewPost);
			socket.off('post_deleted', handlePostDeletedSocket);
		};
	});

	onDestroy(() => {
		if (typeof document !== 'undefined') {
			document.removeEventListener('postDeleted', handlePostDeleted);
		}
	});
</script>

<div class="p-4 md:p-8 min-h-screen w-full bg-gray-50 md:ml-20">
	<div class="max-w-2xl mx-auto">
		<h1 class="text-2xl md:text-3xl font-bold text-gray-900 mb-6">Feed</h1>

		{#if posts.length === 0}
			<div class="text-center py-12">
				<p class="text-gray-500">No posts yet. Be the first to share something!</p>
			</div>
		{:else}
			<div class="space-y-4">
				{#each posts as post (post.id)}
					<Post post={{ ...post, current_user_id: data.currentUserId, current_username: data.currentUsername }} />
				{/each}
			</div>
		{/if}
	</div>
</div>

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
		friends: Array<{
			id: number;
			username: string;
			is_online: boolean;
			last_seen: string | null;
		}>;
	}

	let { data }: { data: PageData } = $props();
	let posts = $state(data.posts);
	let socket: Socket;
	let mounted = $state(false);

	// Track pending friend posts
	let pendingFriendPosts = $state<any[]>([]);
	let newFriendPostsCount = $state(0);

	// Create a Set of friend IDs for quick lookup
	let friendIds = $state(new Set(data.friends.map(f => f.id)));

	function handlePostDeleted(event: any) {
		const postId = event.detail.postId;
		posts = posts.filter(p => p.id !== postId);
	}

	function loadNewFriendPosts() {
		// Prepend all pending friend posts to the feed
		posts = [...pendingFriendPosts, ...posts];

		// Clear pending posts
		pendingFriendPosts = [];
		newFriendPostsCount = 0;

		// Scroll to top smoothly
		window.scrollTo({ top: 0, behavior: 'smooth' });
	}

	onMount(() => {
		// Trigger mounted state for fade-in animation
		mounted = true;

		document.addEventListener('postDeleted', handlePostDeleted);

		// Connect to socket for real-time updates
		socket = getSocket();

		// Fetch initial unread message status
		fetchUnreadMessageStatus();

		const handleNewPost = (postData: any) => {
			console.log('New post received:', postData);
			// Check if post already exists to avoid duplicates
			const postAlreadyExists = posts.some(p => p.id === postData.post_id) ||
			                          pendingFriendPosts.some(p => p.id === postData.post_id);

			if (!postAlreadyExists) {
				// Check if the post is from a friend
				const isFromFriend = friendIds.has(postData.post_data.owner_id);

				if (isFromFriend) {
					// Add to pending friend posts instead of directly to feed
					pendingFriendPosts = [postData.post_data, ...pendingFriendPosts];
					newFriendPostsCount = pendingFriendPosts.length;
				} else {
					// Non-friend posts are added directly to the feed
					posts = [postData.post_data, ...posts];
				}
			}
		};

		const handlePostDeletedSocket = (data: any) => {
			console.log('Post deleted via socket:', data);
			// Remove the deleted post from the feed
			posts = posts.filter(p => p.id !== data.post_id);
			// Also remove from pending friend posts if it's there
			pendingFriendPosts = pendingFriendPosts.filter(p => p.id !== data.post_id);
			newFriendPostsCount = pendingFriendPosts.length;
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

<div class="p-4 md:p-8 min-h-screen w-full bg-gray-200 md:ml-20">
	<div class="max-w-2xl mx-auto">
		<h1 class="text-2xl md:text-3xl font-bold text-gray-900 mb-6">Feed</h1>

		<!-- New friend posts button (fixed at top) -->
		{#if newFriendPostsCount > 0}
			<div class="fixed top-4 left-1/2 transform -translate-x-1/2 z-50 animate-slide-down md:left-[calc(50%+2.5rem)]">
				<button
					onclick={loadNewFriendPosts}
					class="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white text-sm font-medium rounded-full shadow-lg transition-all duration-200 hover:shadow-xl active:scale-95 flex items-center gap-2"
				>
					<svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" viewBox="0 0 20 20" fill="currentColor">
						<path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm1-11a1 1 0 10-2 0v3.586L7.707 9.293a1 1 0 00-1.414 1.414l3 3a1 1 0 001.414 0l3-3a1 1 0 00-1.414-1.414L11 10.586V7z" clip-rule="evenodd" />
					</svg>
					<span class="whitespace-nowrap">
						{newFriendPostsCount === 1 ? '1 new post' : `${newFriendPostsCount} new posts`}
					</span>
				</button>
			</div>
		{/if}

		{#if posts.length === 0}
			<div class="text-center py-12">
				<p class="text-gray-500">No posts yet. Be the first to share something!</p>
			</div>
		{:else}
			<div class="space-y-4">
				{#each posts as post, index (post.id)}
					<div class="post-fade-in" style="animation-delay: {mounted ? 0 : index * 50}ms;">
						<Post post={{ ...post, current_user_id: data.currentUserId, current_username: data.currentUsername }} />
					</div>
				{/each}
			</div>
		{/if}
	</div>
</div>

<style>
	@keyframes slide-down {
		from {
			opacity: 0;
			transform: translate(-50%, -20px);
		}
		to {
			opacity: 1;
			transform: translate(-50%, 0);
		}
	}

	.animate-slide-down {
		animation: slide-down 0.3s ease-out;
	}

	@keyframes post-fade {
		from {
			opacity: 0;
			transform: translateY(20px);
		}
		to {
			opacity: 1;
			transform: translateY(0);
		}
	}

	.post-fade-in {
		animation: post-fade 0.4s ease-out forwards;
		opacity: 0;
	}

	@media (min-width: 768px) {
		@keyframes slide-down {
			from {
				opacity: 0;
				transform: translate(-50%, -20px);
			}
			to {
				opacity: 1;
				transform: translate(-50%, 0);
			}
		}
	}
</style>

<script lang="ts">
	import { onMount } from 'svelte';
	import { goto } from '$app/navigation';
	import Post from '$lib/components/Post.svelte';

	interface PageData {
		user_id: number;
		username: string;
		display_name?: string;
		bio?: string;
		avatar_path?: string;
		is_online: boolean;
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

	function handlePostDeleted(event: any) {
		const postId = event.detail.postId;
		posts = posts.filter(p => p.id !== postId);
	}

	function goBack() {
		goto('/');
	}

	onMount(() => {
		document.addEventListener('postDeleted', handlePostDeleted);

		return () => {
			document.removeEventListener('postDeleted', handlePostDeleted);
		};
	});
</script>

<div class="p-4 md:p-8 min-h-screen w-full md:ml-20">
	<div class="max-w-2xl mx-auto">
		<!-- Back Button -->
		<button
			onclick={goBack}
			class="mb-4 flex items-center gap-2 text-gray-600 hover:text-gray-900 transition-colors"
		>
			<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
				<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7"/>
			</svg>
			<span class="text-sm font-medium">Back</span>
		</button>

		<!-- Profile Header -->
		<div class="bg-white rounded-lg border border-gray-200 p-6 mb-6 shadow-soft-md">
			<div class="flex flex-col md:flex-row items-center md:items-start gap-6">
				<div class="relative">
					<div class="w-32 h-32 rounded-full bg-gradient-to-br from-blue-400 to-indigo-400 flex items-center justify-center text-white font-bold text-4xl overflow-hidden">
						{#if data.avatar_path}
							<img src="http://localhost:5000/static/{data.avatar_path}" alt={data.username} class="w-full h-full object-cover" />
						{:else}
							{data.username.substring(0, 2).toUpperCase()}
						{/if}
					</div>
					{#if data.is_online}
						<div class="absolute bottom-2 right-2 w-6 h-6 bg-green-500 border-4 border-white rounded-full"></div>
					{/if}
				</div>
				<div class="flex-1 text-center md:text-left">
					<h1 class="text-3xl font-bold text-gray-900 mb-1">{data.display_name || data.username}</h1>
					<p class="text-base text-gray-500 mb-3">@{data.username}</p>
					{#if data.bio}
						<p class="text-sm text-gray-700 mb-3 max-w-md">{data.bio}</p>
					{/if}
					<div class="flex items-center gap-4 text-sm text-gray-600 justify-center md:justify-start">
						<span class="font-semibold">{posts.length} {posts.length === 1 ? 'post' : 'posts'}</span>
						<span class="flex items-center gap-1">
							<div class="w-2 h-2 rounded-full {data.is_online ? 'bg-green-500' : 'bg-gray-400'}"></div>
							{data.is_online ? 'Online' : 'Offline'}
						</span>
					</div>
				</div>
			</div>
		</div>

		<!-- Posts -->
		<div>
			<h2 class="text-lg font-semibold text-gray-900 mb-4">Posts</h2>
			{#if posts.length === 0}
				<div class="bg-white rounded-lg border border-gray-200 p-12 text-center shadow-soft-md">
					<svg class="w-16 h-16 mx-auto text-gray-300 mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
						<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z"/>
					</svg>
					<h3 class="text-base font-semibold text-gray-900 mb-1">No posts yet</h3>
					<p class="text-sm text-gray-500">This user hasn't shared anything</p>
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
</div>

<script lang="ts">
	import { onMount, onDestroy } from 'svelte';
	import { goto } from '$app/navigation';
	import Post from '$lib/components/Post.svelte';

	interface PageData {
		username: string;
		posts: Array<{
			id: number;
			owner_id: number;
			owner_name: string;
			image_path: string;
			created_at: string;
			likes: Array<{ user_id: number; username: string }>;
		}>;
		currentUserId: number;
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
	});

	onDestroy(() => {
		document.removeEventListener('postDeleted', handlePostDeleted);
	});
</script>

<div class="p-4 md:p-8 min-h-screen w-full bg-gray-50 md:ml-20">
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
		<div class="bg-white rounded-lg border border-gray-200 p-6 mb-6">
			<div class="flex items-center gap-4">
				<div class="w-20 h-20 rounded-full bg-gradient-to-br from-blue-400 to-indigo-400 flex items-center justify-center text-white font-bold text-2xl">
					{data.username.substring(0, 2).toUpperCase()}
				</div>
				<div>
					<h1 class="text-2xl font-bold text-gray-900">{data.username}</h1>
					<p class="text-sm text-gray-500">{posts.length} {posts.length === 1 ? 'post' : 'posts'}</p>
				</div>
			</div>
		</div>

		<!-- Posts -->
		<div>
			<h2 class="text-lg font-semibold text-gray-900 mb-4">Posts</h2>
			{#if posts.length === 0}
				<div class="bg-white rounded-lg border border-gray-200 p-12 text-center">
					<svg class="w-16 h-16 mx-auto text-gray-300 mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
						<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z"/>
					</svg>
					<h3 class="text-base font-semibold text-gray-900 mb-1">No posts yet</h3>
					<p class="text-sm text-gray-500">This user hasn't shared anything</p>
				</div>
			{:else}
				<div class="space-y-4">
					{#each posts as post (post.id)}
						<Post post={{ ...post, current_user_id: data.currentUserId }} />
					{/each}
				</div>
			{/if}
		</div>
	</div>
</div>

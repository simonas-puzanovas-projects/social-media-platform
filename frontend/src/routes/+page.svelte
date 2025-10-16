<script lang="ts">
	import Post from '$lib/components/Post.svelte';

	interface PageData {
		posts: Array<{
			id: number;
			owner_name: string;
			image_path: string;
			created_at: string;
			likes: Array<{ user_id: number; username: string }>;
		}>;
		currentUserId: number;
	}

	let { data }: { data: PageData } = $props();
</script>

<div class="p-4 md:p-8 min-h-screen w-full bg-gray-50">
	<div class="max-w-2xl mx-auto">
		<h1 class="text-2xl md:text-3xl font-bold text-gray-900 mb-6">Feed</h1>

		{#if data.posts.length === 0}
			<div class="text-center py-12">
				<p class="text-gray-500">No posts yet. Be the first to share something!</p>
			</div>
		{:else}
			<div class="space-y-4">
				{#each data.posts as post}
					<Post post={{ ...post, current_user_id: data.currentUserId }} />
				{/each}
			</div>
		{/if}
	</div>
</div>

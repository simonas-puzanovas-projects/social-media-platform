<script lang="ts">
	interface PostProps {
		id: number;
		owner_name: string;
		image_path: string;
		created_at: string;
		likes: Array<{ user_id: number; username: string }>;
		current_user_id?: number;
	}

	let { post }: { post: PostProps } = $props();

	let likeCount = $state(post.likes.length);
	let isLiked = $state(post.likes.some(like => like.user_id === post.current_user_id));

	async function handleLike() {
		try {
			const response = await fetch(`http://localhost:5000/api/like_post/${post.id}`, {
				method: 'POST',
				credentials: 'include'
			});

			if (response.ok) {
				const newCount = await response.text();
				likeCount = parseInt(newCount);
				isLiked = !isLiked;
			}
		} catch (error) {
			console.error('Failed to like post:', error);
		}
	}
</script>

<article class="bg-white rounded-lg border border-gray-200 overflow-hidden">
	<!-- Post Header -->
	<div class="p-4 flex items-center gap-3">
		<div class="w-10 h-10 bg-gray-300 rounded-full flex items-center justify-center">
			<span class="text-sm font-medium text-gray-600">{post.owner_name[0].toUpperCase()}</span>
		</div>
		<div>
			<h3 class="font-medium text-gray-900">{post.owner_name}</h3>
			<p class="text-xs text-gray-500">{new Date(post.created_at).toLocaleDateString()}</p>
		</div>
	</div>

	<!-- Post Image -->
	<img
		src="http://localhost:5000/static/{post.image_path}"
		alt="Post by {post.owner_name}"
		class="w-full object-cover"
	/>

	<!-- Post Actions -->
	<div class="p-4">
		<button
			onclick={handleLike}
			class="flex items-center gap-2 text-gray-700 hover:text-red-500 transition-colors"
		>
			<svg
				class="w-6 h-6"
				fill={isLiked ? "currentColor" : "none"}
				stroke="currentColor"
				viewBox="0 0 24 24"
			>
				<path
					stroke-linecap="round"
					stroke-linejoin="round"
					stroke-width="2"
					d="M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z"
				/>
			</svg>
			<span class="text-sm font-medium">{likeCount}</span>
		</button>
	</div>
</article>

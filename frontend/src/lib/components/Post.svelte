<script lang="ts">
	import { onMount, onDestroy } from 'svelte';
	import { fly, fade } from 'svelte/transition';
	import { getSocket } from '$lib/socket';
	import type { Socket } from 'socket.io-client';

	interface PostProps {
		id: number;
		owner_name: string;
		image_path: string;
		created_at: string;
		likes: Array<{ user_id: number; username: string }>;
		current_user_id?: number;
		current_username?: string;
		owner_id?: number;
		comment_count?: number;
	}

	interface Comment {
		id: number;
		user_id: number;
		username: string;
		content: string;
		created_at: string;
		parent_id: number | null;
		replies: Comment[];
	}

	let { post }: { post: PostProps } = $props();

	let likeCount = $state(post.likes.length);
	let isLiked = $state(post.likes.some(like => like.user_id === post.current_user_id));
	let showComments = $state(false);
	let comments: Comment[] = $state([]);
	let commentCount = $state(post.comment_count || 0);
	let newComment = $state('');
	let replyingTo: number | null = $state(null);
	let replyContent = $state('');
	let loadingComments = $state(false);
	let postingComment = $state(false);
	let commentError = $state('');
	let expandedReplies = $state<Set<number>>(new Set());
	let socket: Socket;
	let commentsLoaded = $state(false);

	async function handleLike() {
		try {
			// Store the current state before making the request
			const wasLikedBefore = isLiked;

			const response = await fetch(`http://localhost:5000/api/like_post/${post.id}`, {
				method: 'POST',
				credentials: 'include'
			});

			if (response.ok) {
				const newCount = await response.text();
				const newCountInt = parseInt(newCount);
				// Toggle the like state - if we were liked before, now we're unliked and vice versa
				isLiked = !wasLikedBefore;
				likeCount = newCountInt;
			}
		} catch (error) {
			console.error('Failed to like post:', error);
		}
	}

	async function toggleComments() {
		showComments = !showComments;
		if (showComments && comments.length === 0) {
			await loadComments();
		} else if (!showComments) {
			// Reset animation state when closing
			commentsLoaded = false;
		}
	}

	async function loadComments() {
		try {
			loadingComments = true;
			commentError = '';
			const response = await fetch(`http://localhost:5000/api/comments/${post.id}`, {
				credentials: 'include'
			});

			if (response.ok) {
				const data = await response.json();
				// Backend already provides nested structure via to_dict()
				comments = data.comments;
				// Count all comments including nested replies
				const countAllComments = (comms: Comment[]): number => {
					return comms.reduce((total, comment) => {
						return total + 1 + (comment.replies ? countAllComments(comment.replies) : 0);
					}, 0);
				};
				commentCount = countAllComments(data.comments);
				// Trigger animation
				setTimeout(() => {
					commentsLoaded = true;
				}, 50);
			}
		} catch (error) {
			console.error('Failed to load comments:', error);
			commentError = 'Failed to load comments';
		} finally {
			loadingComments = false;
		}
	}

	async function postComment() {
		if (!newComment.trim()) return;

		const content = newComment.trim();
		newComment = ''; // Clear input immediately for better UX

		try {
			postingComment = true;
			commentError = '';

			const response = await fetch(`http://localhost:5000/api/comment/${post.id}`, {
				method: 'POST',
				credentials: 'include',
				headers: { 'Content-Type': 'application/json' },
				body: JSON.stringify({ comment: content })
			});

			if (response.ok) {
				const data = await response.json();
				// Add comment to UI immediately (socket event will be ignored due to duplicate check)
				const commentExists = comments.some(c => c.id === data.comment.id);
				if (!commentExists) {
					comments = [data.comment, ...comments];
					commentCount += 1;
				}
			} else {
				newComment = content; // Restore on error
				const data = await response.json();
				commentError = data.message || 'Failed to post comment';
			}
		} catch (error) {
			newComment = content; // Restore on error
			console.error('Failed to post comment:', error);
			commentError = 'Failed to post comment';
		} finally {
			postingComment = false;
		}
	}

	async function postReply(parentId: number) {
		if (!replyContent.trim()) return;

		const content = replyContent.trim();
		replyContent = ''; // Clear input immediately
		replyingTo = null;

		try {
			postingComment = true;
			commentError = '';

			const response = await fetch(`http://localhost:5000/api/comment/${post.id}`, {
				method: 'POST',
				credentials: 'include',
				headers: { 'Content-Type': 'application/json' },
				body: JSON.stringify({
					comment: content,
					parent_id: parentId
				})
			});

			if (response.ok) {
				const data = await response.json();
				// Add reply to parent comment (socket event will be ignored due to duplicate check)
				comments = comments.map(c => {
					if (c.id === parentId) {
						const replyExists = c.replies.some(r => r.id === data.comment.id);
						if (!replyExists) {
							return { ...c, replies: [...c.replies, data.comment] };
						}
					}
					return c;
				});
				// Expand parent to show new reply
				expandedReplies = new Set([...expandedReplies, parentId]);
				commentCount += 1;
			} else {
				replyContent = content; // Restore on error
				replyingTo = parentId;
				const data = await response.json();
				commentError = data.message || 'Failed to post reply';
			}
		} catch (error) {
			replyContent = content; // Restore on error
			replyingTo = parentId;
			console.error('Failed to post reply:', error);
			commentError = 'Failed to post reply';
		} finally {
			postingComment = false;
		}
	}

	async function deleteComment(commentId: number) {
		if (!confirm('Are you sure you want to delete this comment?')) return;

		// Store backup for potential rollback
		const commentsBackup = JSON.parse(JSON.stringify(comments));
		const countBackup = commentCount;

		try {
			// Optimistic update - remove comment immediately
			const removeComment = (commentList: Comment[], id: number): { comments: Comment[], count: number } => {
				let removedCount = 0;
				const filtered = commentList.filter(c => {
					if (c.id === id) {
						// Count this comment and all its replies
						removedCount = 1 + countReplies(c.replies);
						return false;
					}
					if (c.replies && c.replies.length > 0) {
						const result = removeComment(c.replies, id);
						c.replies = result.comments;
						removedCount += result.count;
					}
					return true;
				});
				return { comments: filtered, count: removedCount };
			};

			const countReplies = (replies: Comment[]): number => {
				return replies.reduce((total, reply) => {
					return total + 1 + countReplies(reply.replies || []);
				}, 0);
			};

			const result = removeComment(comments, commentId);
			comments = result.comments;
			commentCount -= result.count;

			const response = await fetch(`http://localhost:5000/api/comment/${commentId}`, {
				method: 'DELETE',
				credentials: 'include'
			});

			if (!response.ok) {
				// Revert on error
				comments = commentsBackup;
				commentCount = countBackup;
				const data = await response.json();
				commentError = data.message || 'Failed to delete comment';
			}
		} catch (error) {
			// Revert on error
			comments = commentsBackup;
			commentCount = countBackup;
			console.error('Failed to delete comment:', error);
			commentError = 'Failed to delete comment';
		}
	}

	function formatDate(dateString: string) {
		const date = new Date(dateString);
		const now = new Date();
		const diff = now.getTime() - date.getTime();
		const minutes = Math.floor(diff / (1000 * 60));
		const hours = Math.floor(diff / (1000 * 60 * 60));
		const days = Math.floor(diff / (1000 * 60 * 60 * 24));

		if (minutes < 1) return 'just now';
		if (minutes < 60) return `${minutes}m ago`;
		if (hours < 24) return `${hours}h ago`;
		if (days === 1) return 'yesterday';
		if (days < 7) return `${days}d ago`;
		return date.toLocaleDateString();
	}

	function startReply(commentId: number) {
		replyingTo = commentId;
		replyContent = '';
	}

	function cancelReply() {
		replyingTo = null;
		replyContent = '';
	}

	function toggleReplies(commentId: number) {
		const newExpanded = new Set(expandedReplies);
		if (newExpanded.has(commentId)) {
			newExpanded.delete(commentId);
		} else {
			newExpanded.add(commentId);
		}
		expandedReplies = newExpanded;
	}

	async function deletePost() {
		if (!confirm('Are you sure you want to delete this post?')) return;

		try {
			const response = await fetch('http://localhost:5000/delete_post', {
				method: 'POST',
				credentials: 'include',
				headers: { 'Content-Type': 'application/json' },
				body: JSON.stringify({ post_id: post.id })
			});

			const data = await response.json();

			if (response.ok && data.success) {
				// Dispatch custom event to remove post from parent
				const event = new CustomEvent('postDeleted', {
					detail: { postId: post.id },
					bubbles: true
				});
				document.dispatchEvent(event);
			} else {
				alert(data.message || 'Failed to delete post');
			}
		} catch (error) {
			console.error('Failed to delete post:', error);
			alert('An error occurred while deleting the post');
		}
	}

	onMount(() => {
		socket = getSocket();

		// Handle post liked events
		const handlePostLiked = (data: any) => {
			if (data.post_id === post.id) {
				likeCount = data.like_count;
				// Update isLiked if the current user liked it
				if (data.user_id === post.current_user_id) {
					isLiked = true;
				}
			}
		};

		// Handle post unliked events
		const handlePostUnliked = (data: any) => {
			if (data.post_id === post.id) {
				likeCount = data.like_count;
				// Update isLiked if the current user unliked it
				if (data.user_id === post.current_user_id) {
					isLiked = false;
				}
			}
		};

		// Handle new comment events
		const handlePostCommented = (data: any) => {
			if (data.post_id !== post.id) return;

			// Update comment count from server
			commentCount = data.comment_count;

			// Only update UI if comments section is visible
			if (!showComments) return;

			if (data.is_reply) {
				// Add reply to parent comment (with duplicate check)
				const parentId = data.comment.parent_id;
				comments = comments.map(c => {
					if (c.id === parentId) {
						const replyExists = c.replies.some(r => r.id === data.comment.id);
						if (!replyExists) {
							expandedReplies = new Set([...expandedReplies, parentId]);
							return { ...c, replies: [...c.replies, data.comment] };
						}
					}
					return c;
				});
			} else {
				// Add top-level comment (with duplicate check)
				const commentExists = comments.some(c => c.id === data.comment.id);
				if (!commentExists) {
					comments = [data.comment, ...comments];
				}
			}
		};

		// Handle comment deletion events
		const handleCommentDeleted = (data: any) => {
			if (data.post_id !== post.id) return;

			// Update comment count from server
			commentCount = data.comment_count;

			// Only update UI if comments section is visible
			if (!showComments) return;

			// Recursively remove comment from nested structure
			const removeComment = (commentList: Comment[], commentId: number): Comment[] => {
				return commentList.filter(c => {
					if (c.id === commentId) return false;
					if (c.replies) {
						c.replies = removeComment(c.replies, commentId);
					}
					return true;
				});
			};
			comments = removeComment(comments, data.comment_id);
		};

		socket.on('post_liked', handlePostLiked);
		socket.on('post_unliked', handlePostUnliked);
		socket.on('post_commented', handlePostCommented);
		socket.on('post_comment_deleted', handleCommentDeleted);

		return () => {
			socket.off('post_liked', handlePostLiked);
			socket.off('post_unliked', handlePostUnliked);
			socket.off('post_commented', handlePostCommented);
			socket.off('post_comment_deleted', handleCommentDeleted);
		};
	});
</script>

<article class="bg-white rounded-lg border border-gray-200 overflow-hidden">
	<!-- Post Header -->
	<div class="p-4 flex items-center justify-between">
		<a href="/profile/{post.owner_name}" class="flex items-center gap-3 hover:opacity-80 transition-opacity">
			<div class="w-10 h-10 bg-gray-300 rounded-full flex items-center justify-center">
				<span class="text-sm font-medium text-gray-600">{post.owner_name[0].toUpperCase()}</span>
			</div>
			<div>
				<h3 class="font-medium text-gray-900">{post.owner_name}</h3>
				<p class="text-xs text-gray-500">{new Date(post.created_at).toLocaleDateString()}</p>
			</div>
		</a>
		{#if post.owner_id === post.current_user_id}
			<button
				onclick={deletePost}
				class="p-2 text-gray-400 hover:text-red-500 hover:bg-red-50 rounded-lg transition-colors"
				title="Delete post"
			>
				<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
					<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"/>
				</svg>
			</button>
		{/if}
	</div>

	<!-- Post Image -->
	<img
		src="http://localhost:5000/static/{post.image_path}"
		alt="Post by {post.owner_name}"
		class="w-full object-cover"
	/>

	<!-- Post Actions -->
	<div class="p-4 border-b border-gray-100">
		<div class="flex items-center gap-4">
			<button
				onclick={handleLike}
				class="flex items-center gap-2 transition-colors"
				class:text-red-500={isLiked}
				class:text-gray-700={!isLiked}
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
			<button
				onclick={toggleComments}
				class="flex items-center gap-2 text-gray-700 hover:text-blue-500 transition-colors"
			>
				<svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
					<path
						stroke-linecap="round"
						stroke-linejoin="round"
						stroke-width="2"
						d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z"
					/>
				</svg>
				<span class="text-sm font-medium">{commentCount} {commentCount === 1 ? 'comment' : 'comments'}</span>
			</button>
		</div>
	</div>

	<!-- Comments Section -->
	{#if showComments}
		<div class="p-4 bg-gray-50">
			{#if commentError}
				<div class="mb-3 p-2 bg-red-50 border border-red-200 rounded text-xs text-red-800" transition:fade="{{ duration: 200 }}">
					{commentError}
				</div>
			{/if}

			<!-- New Comment Input -->
			<div class="mb-4">
				<div class="flex gap-2">
					<input
						type="text"
						bind:value={newComment}
						placeholder="Write a comment..."
						onkeydown={(e) => e.key === 'Enter' && postComment()}
						class="flex-1 px-3 py-2 bg-white border border-gray-300 rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
					/>
					<button
						onclick={postComment}
						disabled={postingComment || !newComment.trim()}
						class="px-4 py-2 bg-blue-500 text-white text-sm font-medium rounded-md hover:bg-blue-600 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
					>
						{postingComment ? '...' : 'Post'}
					</button>
				</div>
			</div>

			<!-- Comments List -->
			{#if loadingComments}
				<div class="text-center py-4 text-gray-500 text-sm">Loading comments...</div>
			{:else if comments.length === 0}
				<div class="text-center py-4 text-gray-500 text-sm">No comments yet. Be the first!</div>
			{:else}
				<div class="space-y-4">
					{#each comments as comment, index (comment.id)}
						<div class="bg-white rounded-lg p-3 comment-fade-in" style="animation-delay: {commentsLoaded ? 0 : index * 50}ms;">
							<!-- Comment -->
							<div class="flex gap-2">
								<div class="w-8 h-8 rounded-full bg-gradient-to-br from-blue-400 to-indigo-400 flex items-center justify-center text-white font-medium text-xs flex-shrink-0">
									{comment.username[0].toUpperCase()}
								</div>
								<div class="flex-1 min-w-0">
									<div class="flex items-center gap-2 mb-1">
										<span class="font-semibold text-sm text-gray-900">{comment.username}</span>
										<span class="text-xs text-gray-500">{formatDate(comment.created_at)}</span>
									</div>
									<p class="text-sm text-gray-700 mb-2">{comment.content}</p>
									<div class="flex items-center gap-3">
										<button
											onclick={() => startReply(comment.id)}
											class="text-xs text-gray-500 hover:text-blue-500 font-medium"
										>
											Reply
										</button>
										{#if comment.replies.length > 0}
											<button
												onclick={() => toggleReplies(comment.id)}
												class="text-xs text-gray-500 hover:text-blue-500 font-medium flex items-center gap-1"
											>
												<span>{expandedReplies.has(comment.id) ? '▼' : '▶'}</span>
												<span>{comment.replies.length} {comment.replies.length === 1 ? 'reply' : 'replies'}</span>
											</button>
										{/if}
										{#if comment.user_id === post.current_user_id}
											<button
												onclick={() => deleteComment(comment.id)}
												class="text-xs text-gray-500 hover:text-red-500 font-medium"
											>
												Delete
											</button>
										{/if}
									</div>

									<!-- Reply Input -->
									{#if replyingTo === comment.id}
										<div class="mt-3 flex gap-2" transition:fly="{{ y: -10, duration: 200 }}">
											<input
												type="text"
												bind:value={replyContent}
												placeholder="Write a reply..."
												onkeydown={(e) => e.key === 'Enter' && postReply(comment.id)}
												class="flex-1 px-3 py-1.5 bg-gray-50 border border-gray-300 rounded text-xs focus:outline-none focus:ring-2 focus:ring-blue-500"
											/>
											<button
												onclick={() => postReply(comment.id)}
												disabled={postingComment || !replyContent.trim()}
												class="px-3 py-1.5 bg-blue-500 text-white text-xs font-medium rounded hover:bg-blue-600 transition-colors disabled:opacity-50"
											>
												Reply
											</button>
											<button
												onclick={cancelReply}
												class="px-3 py-1.5 bg-gray-100 text-gray-700 text-xs font-medium rounded hover:bg-gray-200 transition-colors"
											>
												Cancel
											</button>
										</div>
									{/if}

									<!-- Nested Replies -->
									{#if comment.replies.length > 0 && expandedReplies.has(comment.id)}
										<div class="mt-3 space-y-3 pl-4 border-l-2 border-gray-200">
											{#each comment.replies as reply, replyIndex (reply.id)}
												<div class="flex gap-2 reply-fade-in" style="animation-delay: {replyIndex * 40}ms;">
													<div class="w-7 h-7 rounded-full bg-gradient-to-br from-purple-400 to-pink-400 flex items-center justify-center text-white font-medium text-xs flex-shrink-0">
														{reply.username[0].toUpperCase()}
													</div>
													<div class="flex-1 min-w-0">
														<div class="flex items-center gap-2 mb-1">
															<span class="font-semibold text-xs text-gray-900">{reply.username}</span>
															<span class="text-xs text-gray-500">{formatDate(reply.created_at)}</span>
														</div>
														<p class="text-xs text-gray-700 mb-1">{reply.content}</p>
														{#if reply.user_id === post.current_user_id}
															<button
																onclick={() => deleteComment(reply.id)}
																class="text-xs text-gray-500 hover:text-red-500 font-medium"
															>
																Delete
															</button>
														{/if}
													</div>
												</div>
											{/each}
										</div>
									{/if}
								</div>
							</div>
						</div>
					{/each}
				</div>
			{/if}
		</div>
	{/if}
</article>

<style>
	@keyframes comment-fade {
		from {
			opacity: 0;
			transform: translateY(15px);
		}
		to {
			opacity: 1;
			transform: translateY(0);
		}
	}

	@keyframes reply-fade {
		from {
			opacity: 0;
			transform: translateX(-10px);
		}
		to {
			opacity: 1;
			transform: translateX(0);
		}
	}

	.comment-fade-in {
		animation: comment-fade 0.4s ease-out forwards;
		opacity: 0;
	}

	.reply-fade-in {
		animation: reply-fade 0.3s ease-out forwards;
		opacity: 0;
	}
</style>

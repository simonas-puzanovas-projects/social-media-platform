<script lang="ts">
	import { onMount } from 'svelte';
	import { postCreationWindowOpen } from '$lib/stores/postCreationStore';
	import { getSocket } from '$lib/socket';
	import type { Socket } from 'socket.io-client';

	let selectedFile: File | null = null;
	let previewUrl: string | null = null;
	let description = '';
	let loading = false;
	let error = '';
	let successMessage = '';
	let fileInput: HTMLInputElement;
	let socket: Socket;

	const MAX_FILE_SIZE = 5 * 1024 * 1024; // 5MB
	const ALLOWED_TYPES = ['image/jpeg', 'image/png', 'image/gif', 'image/webp'];

	function handleFileSelect(event: Event) {
		const target = event.target as HTMLInputElement;
		const file = target.files?.[0];

		if (!file) return;

		// Validate file type
		if (!ALLOWED_TYPES.includes(file.type)) {
			error = 'Please select a valid image file (JPEG, PNG, GIF, or WebP)';
			selectedFile = null;
			previewUrl = null;
			return;
		}

		// Validate file size
		if (file.size > MAX_FILE_SIZE) {
			error = 'Image size must be less than 5MB';
			selectedFile = null;
			previewUrl = null;
			return;
		}

		error = '';
		selectedFile = file;

		// Create preview
		const reader = new FileReader();
		reader.onload = (e) => {
			previewUrl = e.target?.result as string;
		};
		reader.readAsDataURL(file);
	}

	function clearSelection() {
		selectedFile = null;
		previewUrl = null;
		description = '';
		error = '';
		successMessage = '';
		if (fileInput) fileInput.value = '';
	}

	async function handleUpload() {
		if (!selectedFile && !description.trim()) {
			error = 'Please add an image or write something';
			return;
		}

		try {
			loading = true;
			error = '';

			const formData = new FormData();
			if (selectedFile) {
				formData.append('image', selectedFile);
			}
			if (description.trim()) {
				formData.append('description', description.trim());
			}

			const response = await fetch('http://localhost:5000/upload_image', {
				method: 'POST',
				credentials: 'include',
				body: formData
			});

			const data = await response.json();

			if (response.ok && data.success) {
				successMessage = 'Post created successfully!';
				clearSelection();

				// Close window after 1.5 seconds
				setTimeout(() => {
					postCreationWindowOpen.set(false);
					successMessage = '';
				}, 1500);
			} else {
				error = data.message || 'Failed to upload image';
			}
		} catch (err) {
			error = err instanceof Error ? err.message : 'An error occurred while uploading';
		} finally {
			loading = false;
		}
	}

	function handleDrop(event: DragEvent) {
		event.preventDefault();
		const file = event.dataTransfer?.files[0];

		if (!file) return;

		// Create a mock event to reuse validation logic
		const mockEvent = {
			target: {
				files: [file]
			}
		} as any;

		handleFileSelect(mockEvent);
	}

	function handleDragOver(event: DragEvent) {
		event.preventDefault();
	}

	onMount(() => {
		socket = getSocket();

		// Listen for new_post event to refresh feed
		const handleNewPost = (data: any) => {
			console.log('New post created:', data);
		};

		socket.on('new_post', handleNewPost);

		return () => {
			socket.off('new_post', handleNewPost);
		};
	});
</script>

{#if $postCreationWindowOpen}
	<div class="fixed inset-0 backdrop-blur-sm bg-black/30 z-50 flex items-center justify-center md:p-4" on:click={() => postCreationWindowOpen.set(false)}>
		<div class="bg-white md:rounded-lg shadow-xl w-full h-full md:w-[600px] md:h-auto md:max-h-[90vh] flex flex-col" on:click|stopPropagation>
			<!-- Header -->
			<div class="px-6 py-4 border-b border-gray-200 flex items-center justify-between">
				<h1 class="text-xl font-semibold text-gray-900">Create Post</h1>
				<button on:click={() => postCreationWindowOpen.set(false)} class="text-gray-400 hover:text-gray-600">
					<svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
						<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/>
					</svg>
				</button>
			</div>

			{#if error}
				<div class="mx-6 mt-3 p-3 bg-red-50 border border-red-200 rounded-md">
					<p class="text-xs text-red-800">{error}</p>
				</div>
			{/if}
			{#if successMessage}
				<div class="mx-6 mt-3 p-3 bg-green-50 border border-green-200 rounded-md">
					<p class="text-xs text-green-800">{successMessage}</p>
				</div>
			{/if}

			<!-- Content -->
			<div class="flex-1 overflow-y-auto px-6 py-6 pb-20 md:pb-6">
				<div class="space-y-4">
					<!-- Description/Text Input - Always visible -->
					<div>
						<label class="block text-sm font-medium text-gray-700 mb-2">
							What's on your mind?
						</label>
						<textarea
							bind:value={description}
							placeholder="Share your thoughts..."
							rows="4"
							maxlength="500"
							class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-sage-400 focus:border-transparent resize-none"
						></textarea>
						<p class="text-xs text-gray-500 mt-1">{description.length}/500 characters</p>
					</div>

					{#if !previewUrl}
						<!-- Upload Area -->
						<div>
							<label class="block text-sm font-medium text-gray-700 mb-2">
								Add an image (optional)
							</label>
							<div
								class="border-2 border-dashed border-gray-300 rounded-lg p-8 text-center hover:border-gray-400 transition-colors cursor-pointer"
								on:drop={handleDrop}
								on:dragover={handleDragOver}
								on:click={() => fileInput.click()}
							>
								<svg class="w-12 h-12 mx-auto text-gray-400 mb-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
									<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z"/>
								</svg>
								<p class="text-sm text-gray-500 mb-2">Click to upload or drag and drop</p>
								<p class="text-xs text-gray-400">JPEG, PNG, GIF, or WebP (max 5MB)</p>
							</div>
							<input
								type="file"
								bind:this={fileInput}
								on:change={handleFileSelect}
								accept="image/jpeg,image/png,image/gif,image/webp"
								class="hidden"
							/>
						</div>
					{:else}
						<!-- Preview Area -->
						<div class="relative rounded-lg overflow-hidden bg-gray-100">
							<img src={previewUrl} alt="Preview" class="w-full h-auto max-h-96 object-contain"/>
							<button
								on:click={clearSelection}
								class="absolute top-2 right-2 p-2 bg-white rounded-full shadow-lg hover:bg-gray-100 transition-colors"
								title="Remove image"
							>
								<svg class="w-5 h-5 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
									<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/>
								</svg>
							</button>
						</div>
					{/if}

					<!-- Post Button - Always visible -->
					<div class="flex gap-3">
						<button
							on:click={handleUpload}
							disabled={loading}
							class="flex-1 px-4 py-2.5 bg-sage-500 text-white font-medium rounded-md hover:bg-sage-600 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
						>
							{loading ? 'Posting...' : 'Post'}
						</button>
						{#if selectedFile}
							<button
								on:click={clearSelection}
								disabled={loading}
								class="px-4 py-2.5 bg-gray-100 text-gray-700 font-medium rounded-md hover:bg-gray-200 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
							>
								Remove Image
							</button>
						{/if}
					</div>
				</div>
			</div>
		</div>
	</div>
{/if}

<style>
	div::-webkit-scrollbar { width: 8px; }
	div::-webkit-scrollbar-track { background: transparent; }
	div::-webkit-scrollbar-thumb { background: #cbd5e0; border-radius: 4px; }
	div::-webkit-scrollbar-thumb:hover { background: #a0aec0; }
</style>

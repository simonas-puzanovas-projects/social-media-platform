<script lang="ts">
	import { onMount } from 'svelte';
	import Sidebar from '$lib/components/Sidebar.svelte';
	import { goto } from '$app/navigation';

	let { data } = $props();

	let displayName = $state(data.settings.display_name || '');
	let bio = $state(data.settings.bio || '');
	let avatarPreview = $state(data.settings.avatar_path ? `http://localhost:5000/static/${data.settings.avatar_path}` : '');

	let oldPassword = $state('');
	let newPassword = $state('');
	let confirmPassword = $state('');

	let deletePassword = $state('');
	let showDeleteConfirm = $state(false);

	let selectedAvatar: File | null = $state(null);
	let avatarInput: HTMLInputElement;

	let profileLoading = $state(false);
	let passwordLoading = $state(false);
	let avatarLoading = $state(false);
	let deleteLoading = $state(false);

	let profileMessage = $state('');
	let profileError = $state('');
	let passwordMessage = $state('');
	let passwordError = $state('');
	let avatarError = $state('');
	let deleteError = $state('');

	function handleAvatarSelect(event: Event) {
		const target = event.target as HTMLInputElement;
		const file = target.files?.[0];

		if (!file) return;

		const allowedTypes = ['image/jpeg', 'image/png', 'image/gif', 'image/webp'];
		if (!allowedTypes.includes(file.type)) {
			avatarError = 'Please select a valid image file (JPEG, PNG, GIF, or WebP)';
			return;
		}

		if (file.size > 5 * 1024 * 1024) {
			avatarError = 'Image size must be less than 5MB';
			return;
		}

		avatarError = '';
		selectedAvatar = file;

		const reader = new FileReader();
		reader.onload = (e) => {
			avatarPreview = e.target?.result as string;
		};
		reader.readAsDataURL(file);
	}

	async function uploadAvatar() {
		if (!selectedAvatar) return;

		try {
			avatarLoading = true;
			avatarError = '';

			const formData = new FormData();
			formData.append('avatar', selectedAvatar);

			const response = await fetch('http://localhost:5000/api/user/avatar', {
				method: 'POST',
				credentials: 'include',
				body: formData
			});

			const result = await response.json();

			if (response.ok && result.success) {
				avatarPreview = `http://localhost:5000/static/${result.avatar_path}`;
				selectedAvatar = null;
				profileMessage = 'Avatar updated successfully!';
				setTimeout(() => profileMessage = '', 3000);
			} else {
				avatarError = result.message || 'Failed to upload avatar';
			}
		} catch (err) {
			avatarError = 'An error occurred while uploading';
		} finally {
			avatarLoading = false;
		}
	}

	async function updateProfile() {
		try {
			profileLoading = true;
			profileError = '';
			profileMessage = '';

			const response = await fetch('http://localhost:5000/api/user/profile', {
				method: 'POST',
				credentials: 'include',
				headers: { 'Content-Type': 'application/json' },
				body: JSON.stringify({
					display_name: displayName,
					bio: bio
				})
			});

			const result = await response.json();

			if (response.ok && result.success) {
				profileMessage = 'Profile updated successfully!';
				setTimeout(() => profileMessage = '', 3000);
			} else {
				profileError = result.message || 'Failed to update profile';
			}
		} catch (err) {
			profileError = 'An error occurred while updating profile';
		} finally {
			profileLoading = false;
		}
	}

	async function changePassword() {
		if (newPassword !== confirmPassword) {
			passwordError = 'New passwords do not match';
			return;
		}

		if (newPassword.length < 6) {
			passwordError = 'Password must be at least 6 characters';
			return;
		}

		try {
			passwordLoading = true;
			passwordError = '';
			passwordMessage = '';

			const response = await fetch('http://localhost:5000/api/user/password', {
				method: 'POST',
				credentials: 'include',
				headers: { 'Content-Type': 'application/json' },
				body: JSON.stringify({
					old_password: oldPassword,
					new_password: newPassword
				})
			});

			const result = await response.json();

			if (response.ok && result.success) {
				passwordMessage = 'Password changed successfully!';
				oldPassword = '';
				newPassword = '';
				confirmPassword = '';
				setTimeout(() => passwordMessage = '', 3000);
			} else {
				passwordError = result.message || 'Failed to change password';
			}
		} catch (err) {
			passwordError = 'An error occurred while changing password';
		} finally {
			passwordLoading = false;
		}
	}

	async function deleteAccount() {
		if (!deletePassword) {
			deleteError = 'Please enter your password';
			return;
		}

		try {
			deleteLoading = true;
			deleteError = '';

			const response = await fetch('http://localhost:5000/api/user/account', {
				method: 'DELETE',
				credentials: 'include',
				headers: { 'Content-Type': 'application/json' },
				body: JSON.stringify({ password: deletePassword })
			});

			const result = await response.json();

			if (response.ok && result.success) {
				goto('/signin');
			} else {
				deleteError = result.message || 'Failed to delete account';
			}
		} catch (err) {
			deleteError = 'An error occurred while deleting account';
		} finally {
			deleteLoading = false;
		}
	}
</script>

<div class="flex h-screen bg-gray-50">
	<Sidebar />

	<main class="flex-1 overflow-y-auto md:ml-20">
		<div class="max-w-4xl mx-auto px-4 py-8 pb-20 md:pb-8">
			<h1 class="text-3xl font-bold text-gray-900 mb-8">Settings</h1>

			<!-- Profile Section -->
			<div class="bg-white rounded-lg shadow-sm border border-gray-200 p-6 mb-6">
				<h2 class="text-xl font-semibold text-gray-900 mb-4">Profile</h2>

				{#if profileMessage}
					<div class="mb-4 p-3 bg-green-50 border border-green-200 rounded-md">
						<p class="text-sm text-green-800">{profileMessage}</p>
					</div>
				{/if}
				{#if profileError}
					<div class="mb-4 p-3 bg-red-50 border border-red-200 rounded-md">
						<p class="text-sm text-red-800">{profileError}</p>
					</div>
				{/if}

				<!-- Avatar Upload -->
				<div class="mb-6">
					<label class="block text-sm font-medium text-gray-700 mb-2">Profile Picture</label>
					<div class="flex items-center gap-4">
						<div class="w-24 h-24 rounded-full bg-gray-200 overflow-hidden">
							{#if avatarPreview}
								<img src={avatarPreview} alt="Avatar" class="w-full h-full object-cover" />
							{:else}
								<div class="w-full h-full flex items-center justify-center text-gray-400">
									<svg class="w-12 h-12" fill="currentColor" viewBox="0 0 20 20">
										<path fill-rule="evenodd" d="M10 9a3 3 0 100-6 3 3 0 000 6zm-7 9a7 7 0 1114 0H3z" clip-rule="evenodd"/>
									</svg>
								</div>
							{/if}
						</div>
						<div class="flex-1">
							<input
								type="file"
								bind:this={avatarInput}
								on:change={handleAvatarSelect}
								accept="image/jpeg,image/png,image/gif,image/webp"
								class="hidden"
							/>
							<div class="flex gap-2">
								<button
									on:click={() => avatarInput.click()}
									class="px-4 py-2 bg-gray-100 text-gray-700 text-sm font-medium rounded-md hover:bg-gray-200 transition-colors"
								>
									Choose Image
								</button>
								{#if selectedAvatar}
									<button
										on:click={uploadAvatar}
										disabled={avatarLoading}
										class="px-4 py-2 bg-sage-500 text-white text-sm font-medium rounded-md hover:bg-sage-600 transition-colors disabled:opacity-50"
									>
										{avatarLoading ? 'Uploading...' : 'Upload'}
									</button>
								{/if}
							</div>
							{#if avatarError}
								<p class="text-xs text-red-600 mt-1">{avatarError}</p>
							{/if}
							<p class="text-xs text-gray-500 mt-1">JPEG, PNG, GIF, or WebP (max 5MB)</p>
						</div>
					</div>
				</div>

				<!-- Display Name -->
				<div class="mb-4">
					<label for="displayName" class="block text-sm font-medium text-gray-700 mb-2">Display Name</label>
					<input
						id="displayName"
						type="text"
						bind:value={displayName}
						placeholder={data.settings.username}
						class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-sage-500"
					/>
					<p class="text-xs text-gray-500 mt-1">Leave empty to use your username</p>
				</div>

				<!-- Bio -->
				<div class="mb-6">
					<label for="bio" class="block text-sm font-medium text-gray-700 mb-2">Bio</label>
					<textarea
						id="bio"
						bind:value={bio}
						rows="3"
						placeholder="Tell us about yourself..."
						class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-sage-500 resize-none"
					></textarea>
					<p class="text-xs text-gray-500 mt-1">{bio.length}/500 characters</p>
				</div>

				<button
					on:click={updateProfile}
					disabled={profileLoading}
					class="px-6 py-2 bg-sage-500 text-white font-medium rounded-md hover:bg-sage-600 transition-colors disabled:opacity-50"
				>
					{profileLoading ? 'Saving...' : 'Save Profile'}
				</button>
			</div>

			<!-- Security Section -->
			<div class="bg-white rounded-lg shadow-sm border border-gray-200 p-6 mb-6">
				<h2 class="text-xl font-semibold text-gray-900 mb-4">Security</h2>

				{#if passwordMessage}
					<div class="mb-4 p-3 bg-green-50 border border-green-200 rounded-md">
						<p class="text-sm text-green-800">{passwordMessage}</p>
					</div>
				{/if}
				{#if passwordError}
					<div class="mb-4 p-3 bg-red-50 border border-red-200 rounded-md">
						<p class="text-sm text-red-800">{passwordError}</p>
					</div>
				{/if}

				<div class="mb-4">
					<label for="oldPassword" class="block text-sm font-medium text-gray-700 mb-2">Current Password</label>
					<input
						id="oldPassword"
						type="password"
						bind:value={oldPassword}
						class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-sage-500"
					/>
				</div>

				<div class="mb-4">
					<label for="newPassword" class="block text-sm font-medium text-gray-700 mb-2">New Password</label>
					<input
						id="newPassword"
						type="password"
						bind:value={newPassword}
						class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-sage-500"
					/>
				</div>

				<div class="mb-6">
					<label for="confirmPassword" class="block text-sm font-medium text-gray-700 mb-2">Confirm New Password</label>
					<input
						id="confirmPassword"
						type="password"
						bind:value={confirmPassword}
						class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-sage-500"
					/>
				</div>

				<button
					on:click={changePassword}
					disabled={passwordLoading || !oldPassword || !newPassword || !confirmPassword}
					class="px-6 py-2 bg-sage-500 text-white font-medium rounded-md hover:bg-sage-600 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
				>
					{passwordLoading ? 'Changing...' : 'Change Password'}
				</button>
			</div>

			<!-- Danger Zone -->
			<div class="bg-white rounded-lg shadow-sm border border-red-200 p-6">
				<h2 class="text-xl font-semibold text-red-600 mb-2">Danger Zone</h2>
				<p class="text-sm text-gray-600 mb-4">Once you delete your account, there is no going back. Please be certain.</p>

				{#if deleteError}
					<div class="mb-4 p-3 bg-red-50 border border-red-200 rounded-md">
						<p class="text-sm text-red-800">{deleteError}</p>
					</div>
				{/if}

				{#if !showDeleteConfirm}
					<button
						on:click={() => showDeleteConfirm = true}
						class="px-6 py-2 bg-red-500 text-white font-medium rounded-md hover:bg-red-600 transition-colors"
					>
						Delete Account
					</button>
				{:else}
					<div class="border border-red-200 rounded-md p-4 bg-red-50">
						<p class="text-sm font-medium text-red-900 mb-3">Are you absolutely sure?</p>
						<div class="mb-4">
							<label for="deletePassword" class="block text-sm font-medium text-gray-700 mb-2">Enter your password to confirm</label>
							<input
								id="deletePassword"
								type="password"
								bind:value={deletePassword}
								class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-red-500"
							/>
						</div>
						<div class="flex gap-2">
							<button
								on:click={deleteAccount}
								disabled={deleteLoading || !deletePassword}
								class="px-4 py-2 bg-red-600 text-white text-sm font-medium rounded-md hover:bg-red-700 transition-colors disabled:opacity-50"
							>
								{deleteLoading ? 'Deleting...' : 'Yes, Delete My Account'}
							</button>
							<button
								on:click={() => { showDeleteConfirm = false; deletePassword = ''; deleteError = ''; }}
								disabled={deleteLoading}
								class="px-4 py-2 bg-gray-200 text-gray-700 text-sm font-medium rounded-md hover:bg-gray-300 transition-colors disabled:opacity-50"
							>
								Cancel
							</button>
						</div>
					</div>
				{/if}
			</div>
		</div>
	</main>
</div>

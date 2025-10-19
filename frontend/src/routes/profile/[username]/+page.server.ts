import type { PageServerLoad } from './$types';
import { error, redirect } from '@sveltejs/kit';

export const load: PageServerLoad = async ({ params, fetch }) => {
	const { username } = params;

	try {
		const response = await fetch(`http://localhost:5000/api/profile/${username}`, {
			credentials: 'include'
		});

		if (response.status === 401) {
			redirect(303, '/signin');
		}

		if (!response.ok) {
			throw error(404, 'User not found');
		}

		const data = await response.json();

		return {
			user_id: data.user_id,
			username: data.username,
			display_name: data.display_name,
			bio: data.bio,
			avatar_path: data.avatar_path,
			is_online: data.is_online,
			posts: data.posts || [],
			currentUserId: data.current_user_id,
			currentUsername: data.current_username
		};
	} catch (err) {
		if (err instanceof Error && 'status' in err) {
			throw err;
		}
		throw error(404, 'User not found');
	}
};

import type { PageServerLoad } from './$types';
import { error, redirect } from '@sveltejs/kit';

export const load: PageServerLoad = async ({ fetch }) => {
	try {
		const response = await fetch('http://localhost:5000/api/user/settings', {
			credentials: 'include'
		});

		if (response.status === 401) {
			redirect(303, '/signin');
		}

		if (!response.ok) {
			throw error(500, 'Failed to load settings');
		}

		const data = await response.json();

		return {
			settings: data.settings || {}
		};
	} catch (err) {
		if (err instanceof Error && 'status' in err) {
			throw err;
		}
		throw error(500, 'Failed to load settings');
	}
};

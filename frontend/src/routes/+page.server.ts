import type { PageServerLoad } from './$types';
import { redirect } from '@sveltejs/kit';

export const load: PageServerLoad = async ({fetch}) => {

    const response = await fetch('http://localhost:5000/');
    const data = await response.json();

    if (response.status === 401) {
        redirect(303, '/signin');
    }
  
    return { data };
};
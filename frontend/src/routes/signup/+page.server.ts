import { redirect } from '@sveltejs/kit';
import type {Actions} from './$types';

export const actions = {
  default: async ({request}) => {

    const data = await request.formData();
    console.log('Form data:', Object.fromEntries(data));

    const password = data.get("password");
    const repeat_password = data.get("repeat_password");

    if (password != repeat_password){
      return {success: false, message: "The password should be the same as repeated one."}
    }
    
    const response = await fetch('http://localhost:5000/api/signup', {
      method: 'POST',
      body: data
    });

    if (response.ok){
      redirect(302, "/signin")
    }
    
  }
} satisfies Actions;
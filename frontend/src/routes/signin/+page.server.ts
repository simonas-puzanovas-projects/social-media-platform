import {redirect} from '@sveltejs/kit'

export const actions = {

  default: async ({cookies, request}) => {
    console.log('Action triggered!');
    
    const data = await request.formData();
    
    const response = await fetch('http://localhost:5000/api/signin', {
      method: 'POST',
      credentials: 'include',
      body: data
    });


    const response_data = await response.json()

    //extracting and setting session cookie because flask session is headache
    const setCookieHeader = response.headers.get('set-cookie');

    if (response_data.success && setCookieHeader) {
      const sessionMatch = setCookieHeader.match(/session=([^;]+)/);

      if (sessionMatch) {
        const sessionValue = sessionMatch[1];

        cookies.set("session", sessionValue, {
          path: "/",
          httpOnly: true,
          secure: false, // Set to true in production with HTTPS
          sameSite: "lax",
          maxAge: 60 * 60 * 24 * 7 // 7 days
        })
        redirect(302, '/');
      }
    }

    return { success: response_data.success, message: response_data.message };
  }

}
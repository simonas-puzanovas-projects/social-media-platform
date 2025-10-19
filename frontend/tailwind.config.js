/** @type {import('tailwindcss').Config} */
export default {
	content: ['./src/**/*.{html,js,svelte,ts}'],
	theme: {
		extend: {
			colors: {
				sage: {
					50: '#F5F8F6',
					100: '#E8F0EC',
					200: '#D1E1D8',
					300: '#B8D4C6',
					400: '#9DB8A6',
					500: '#7FA391',
					600: '#6A8C7C',
					700: '#547061',
					800: '#3F5447',
					900: '#2A3830'
				}
			},
			boxShadow: {
				'soft': '0 1px 3px 0 rgba(0, 0, 0, 0.05), 0 1px 2px 0 rgba(0, 0, 0, 0.03)',
				'soft-md': '0 4px 6px -1px rgba(0, 0, 0, 0.05), 0 2px 4px -1px rgba(0, 0, 0, 0.03)',
				'soft-lg': '0 10px 15px -3px rgba(0, 0, 0, 0.05), 0 4px 6px -2px rgba(0, 0, 0, 0.03)'
			}
		}
	}
};

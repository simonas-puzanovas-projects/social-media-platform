<script lang="ts">
	import '../app.css';
	import favicon from '$lib/assets/favicon.svg';
    import { page } from '$app/state';
	import Sidebar from '$lib/components/Sidebar.svelte';
	let { children } = $props();
</script>

<svelte:head>
	<link rel="icon" href={favicon} />
</svelte:head>



{#if page.url.pathname !== '/signin' && page.url.pathname !== "/signup"}
	{#if page.url.pathname === '/messenger'}
		<main class="flex bg-white h-screen overflow-hidden">
			<Sidebar/>
			{@render children()}
		</main>
	{:else}
		<main class="flex bg-green-50">
			<Sidebar/>
			{@render children()}
		</main>
	{/if}
{:else}
	<main>
		{@render children()}
	</main>
{/if}

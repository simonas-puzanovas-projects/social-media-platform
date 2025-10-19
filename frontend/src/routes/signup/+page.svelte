<script lang="ts">

  import TmpNotify from '$lib/components/TmpNotify.svelte';
  //import type { PageProps } from './$types';

  let {data, form} = $props()

  let username = $state('');
  let password = $state('');
  let repeatPassword = $state('');
  let isPressed = $state(false);

  function handleSubmit(){}

</script>

{#if !form?.success && form?.message}
  <TmpNotify message={form?.message} type="error" position="top-center"></TmpNotify>
{/if}

<div class="min-h-screen bg-gradient-to-br from-slate-50 to-slate-100 flex items-center justify-center p-4">
  <div class="w-full max-w-md">
    <div class="bg-white rounded-2xl shadow-lg p-8 space-y-6">
      <div class="text-center space-y-2">
        <h1 class="text-3xl font-semibold text-slate-800">Create account</h1>
        <p class="text-slate-500">Sign up to get started</p>
      </div>

      <form class="space-y-4" method="POST" autocomplete="off">
        <div class="space-y-2">
          <label for="username" class="block text-sm font-medium text-slate-700">Username</label>
          <input
            id="username"
            type="text"
            bind:value={username}
            name="username"
            class="w-full px-4 py-3 rounded-lg border border-slate-200 focus:border-slate-400 focus:ring-2 focus:ring-slate-200 outline-none transition-all"
            placeholder="johndoe"
          />
        </div>

        <div class="space-y-2">
          <label for="password" class="block text-sm font-medium text-slate-700">Password</label>
          <input
            id="password"
            type="password"
            bind:value={password}
            name="password"
            class="w-full px-4 py-3 rounded-lg border border-slate-200 focus:border-slate-400 focus:ring-2 focus:ring-slate-200 outline-none transition-all"
            placeholder="••••••••"
          />
        </div>

        <div class="space-y-2">
          <label for="repeatPassword" class="block text-sm font-medium text-slate-700">Repeat Password</label>
          <input
            id="repeatPassword"
            type="password"
            bind:value={repeatPassword}
            name="repeat_password"
            class="w-full px-4 py-3 rounded-lg border border-slate-200 focus:border-slate-400 focus:ring-2 focus:ring-slate-200 outline-none transition-all"
            placeholder="••••••••"
            onkeypress={(e) => e.key === 'Enter' && handleSubmit()}
          />
        </div>

        <button
          onclick={handleSubmit}
          onmousedown={() => isPressed = true}
          onmouseup={() => isPressed = false}
          onmouseleave={() => isPressed = false}
          class="w-full py-3 rounded-lg font-medium text-white bg-slate-800 hover:bg-slate-700 transition-all duration-150 {isPressed ? 'scale-95' : 'scale-100'}"
        >
          Sign up
        </button>
      </form>
    </div>

    <p class="text-center mt-6 text-sm text-slate-500">
      Already have an account?
      <a href="/signin" class="text-slate-700 font-medium hover:text-slate-900 transition-colors">Sign in</a>
    </p>
  </div>
</div>
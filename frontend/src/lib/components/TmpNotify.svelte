<script lang="ts">
  import { fly } from 'svelte/transition';

  let { message = 'Notification message', type = 'success', duration = 4000, position = 'top-right' } = $props();

  let visible = $state(true);
  let timeoutId: ReturnType<typeof setTimeout>;
  
  $effect(() => {
    timeoutId = setTimeout(() => {
      visible = false;
    }, duration);
    
    return () => clearTimeout(timeoutId);
  });
  
  function close() {
    clearTimeout(timeoutId);
    visible = false;
  }
  
  function getIcon() {
    switch(type) {
      case 'success': return '✓';
      case 'error': return '✕';
      case 'info': return 'ℹ';
      default: return '✓';
    }
  }
  
  function getStyles() {
    switch(type) {
      case 'success': return 'bg-green-100 border-green-300 text-green-800';
      case 'error': return 'bg-red-100 border-red-300 text-red-800';
      case 'info': return 'bg-blue-100 border-blue-300 text-blue-800';
      default: return 'bg-green-100 border-green-300 text-green-800';
    }
  }

  function getPositionStyles() {
    switch(position) {
      case 'top-center': return 'top-5 left-1/2 -translate-x-1/2';
      case 'top-right': return 'top-5 right-5';
      case 'top-left': return 'top-5 left-5';
      default: return 'top-5 right-5';
    }
  }
</script>

{#if visible}
  <div
    class="fixed min-w-[300px] max-w-[400px] px-5 py-4 rounded-xl flex items-center gap-3 shadow-lg z-[9999] border {getStyles()} {getPositionStyles()}"
    transition:fly={{ y: -20, duration: 300 }}
  >
    <div class="flex-shrink-0 w-6 h-6 flex items-center justify-center rounded-full bg-black bg-opacity-10 text-lg font-bold">
      {getIcon()}
    </div>
    <div class="flex-1 text-sm leading-snug">
      {message}
    </div>
    <button 
      class="flex items-center justify-center w-6 h-6 rounded opacity-60 hover:opacity-100 hover:bg-black hover:bg-opacity-10 transition-opacity"
      onclick={close}
    >
      ✕
    </button>
  </div>
{/if}
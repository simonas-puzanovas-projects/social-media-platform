<script>
    import MessengerFriendsList from "$lib/components/MessengerFriendsList.svelte";
    import ChatWindow from "$lib/components/ChatWindow.svelte";

    let selectedFriendId = null;

    function handleSelectContact(event) {
        selectedFriendId = event.detail;
        // Hide bottom nav on mobile when chat opens
        if (typeof document !== 'undefined') {
            const bottomNav = document.querySelector('.mobile-bottom-nav');
            if (bottomNav) {
                bottomNav.style.display = 'none';
            }
        }
    }

    function handleBackToList() {
        selectedFriendId = null;
        // Show bottom nav on mobile when returning to contacts
        if (typeof document !== 'undefined') {
            const bottomNav = document.querySelector('.mobile-bottom-nav');
            if (bottomNav) {
                bottomNav.style.display = 'block';
            }
        }
    }
</script>

<div class="flex h-screen overflow-hidden w-full">
    <!-- Friends list - hide when chat is selected on mobile -->
    <div class="{selectedFriendId ? 'hidden md:block' : 'block'} w-full md:w-auto">
        <MessengerFriendsList
            bind:selectedContactId={selectedFriendId}
            on:selectContact={handleSelectContact}
        />
    </div>

    <!-- Chat window - full screen on mobile -->
    <div class="flex-1 overflow-hidden {selectedFriendId ? 'block' : 'hidden md:block'}">
        <ChatWindow selectedFriendId={selectedFriendId} onBack={handleBackToList} />
    </div>
</div>
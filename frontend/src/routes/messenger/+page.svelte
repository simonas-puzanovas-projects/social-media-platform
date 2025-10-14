<script>
    import MessengerFriendsList from "$lib/components/MessengerFriendsList.svelte";
    import ChatWindow from "$lib/components/ChatWindow.svelte";

    let selectedFriendId = null;

    function handleSelectContact(event) {
        selectedFriendId = event.detail;
    }
</script>

<div class="flex h-screen overflow-hidden w-full">
    <MessengerFriendsList
        bind:selectedContactId={selectedFriendId}
        on:selectContact={handleSelectContact}
    />
    <div class="flex-1 overflow-hidden">
        <ChatWindow selectedFriendId={selectedFriendId} />
    </div>
</div>
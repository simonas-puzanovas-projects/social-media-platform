import { writable } from 'svelte/store';

export const friendsWindowOpen = writable(false);

function createFriendsRefreshStore() {
    const { subscribe, set, update } = writable({
        shouldRefresh: false,
        timestamp: Date.now()
    });

    return {
        subscribe,
        triggerRefresh: () => {
            update(state => ({
                shouldRefresh: true,
                timestamp: Date.now()
            }));
        },
        reset: () => {
            set({
                shouldRefresh: false,
                timestamp: Date.now()
            });
        }
    };
}

export const friendsRefresh = createFriendsRefreshStore();

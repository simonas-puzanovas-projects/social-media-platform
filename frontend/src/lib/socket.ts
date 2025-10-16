import { io, Socket } from 'socket.io-client';
import { writable } from 'svelte/store';

let socket: Socket | null = null;

export const socketStore = writable<Socket | null>(null);

export function getSocket(): Socket {
	if (!socket) {
		socket = io('http://localhost:5000', {
			withCredentials: true,
			reconnection: true,
			reconnectionDelay: 1000,
			reconnectionAttempts: 5,
			transports: ['polling', 'websocket'] // Try polling first, then upgrade to websocket
		});

		socket.on('connect', () => {
			console.log('Socket connected:', socket?.id);
			socketStore.set(socket);
		});

		socket.on('disconnect', (reason) => {
			console.log('Socket disconnected:', reason);
		});

		socket.on('connect_error', (error) => {
			console.error('Socket connection error:', error);
		});
	}

	return socket;
}

export function disconnectSocket() {
	if (socket) {
		socket.disconnect();
		socket = null;
		socketStore.set(null);
	}
}

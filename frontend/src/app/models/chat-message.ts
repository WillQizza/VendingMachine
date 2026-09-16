export type ChatRole = "user" | "machine";

export interface ChatMessage {
	id: number;
	role: ChatRole;
	content: string;
	/** True while the machine is still streaming this reply. */
	streaming: boolean;
	/** True when the reply is an error notice rather than machine output. */
	error: boolean;
}

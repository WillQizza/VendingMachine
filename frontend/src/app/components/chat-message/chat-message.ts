import { ChangeDetectionStrategy, Component, computed, input } from "@angular/core";

import { ChatMessage } from "../../models/chat-message";

@Component({
	selector: "app-chat-message",
	templateUrl: "./chat-message.html",
	styleUrl: "./chat-message.css",
	changeDetection: ChangeDetectionStrategy.OnPush,
	host: {
		"[class.from-user]": "message().role === 'user'",
		"[class.from-machine]": "message().role === 'machine'",
		"[class.is-error]": "message().error",
	},
})
export class ChatMessageBubble {
	readonly message = input.required<ChatMessage>();

	protected readonly author = computed(() => (this.message().role === "user" ? "You" : "Machine"));
	protected readonly pending = computed(() => {
		const message = this.message();
		return message.streaming && message.content === "";
	});
}

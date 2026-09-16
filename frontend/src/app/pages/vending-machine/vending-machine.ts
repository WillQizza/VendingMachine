import { ChangeDetectionStrategy, Component, DestroyRef, inject, signal } from "@angular/core";
import { takeUntilDestroyed } from "@angular/core/rxjs-interop";

import { ChatPanel } from "../../components/chat-panel/chat-panel";
import { SlotGrid } from "../../components/slot-grid/slot-grid";
import { ChatMessage } from "../../models/chat-message";
import { Slot } from "../../models/slot";
import { ConversationService, ConversationStreamEvent } from "../../services/conversation";
import { InventoryService } from "../../services/inventory";

const WELCOME_MESSAGE = "Hey. Click a slot or tell me what you're in the mood for.";
const OFFLINE_MESSAGE = "The machine isn't responding right now. Try again in a moment.";
const EMPTY_REPLY_MESSAGE = "The machine didn't say anything back. Try asking again.";

@Component({
	selector: "app-vending-machine-page",
	imports: [SlotGrid, ChatPanel],
	templateUrl: "./vending-machine.html",
	styleUrl: "./vending-machine.css",
	changeDetection: ChangeDetectionStrategy.OnPush,
})
export class VendingMachinePage {
	private readonly inventory = inject(InventoryService);
	private readonly conversation = inject(ConversationService);
	private readonly destroyRef = inject(DestroyRef);
	private nextMessageId = 1;

	protected readonly rows = this.inventory.rows;
	protected readonly onlineCount = this.inventory.onlineCount;
	protected readonly inventoryLoading = this.inventory.loading;
	protected readonly inventoryFailed = this.inventory.failed;
	protected readonly busy = signal(false);
	protected readonly messages = signal<ChatMessage[]>([
		this.createMessage("machine", WELCOME_MESSAGE),
	]);

	protected chooseSlot(slot: Slot): void {
		this.send(`I'd like to buy ${slot.name} from slot ${slot.slot}.`);
	}

	protected send(content: string): void {
		const text = content.trim();
		if (text === "" || this.busy()) {
			return;
		}

		const reply = this.createMessage("machine", "", true);
		this.messages.update(messages => [...messages, this.createMessage("user", text), reply]);
		this.busy.set(true);

		this.conversation
			.sendMessage(text)
			.pipe(takeUntilDestroyed(this.destroyRef))
			.subscribe({
				next: event => this.applyStreamEvent(reply.id, event),
				error: () => this.finishReply(reply.id, OFFLINE_MESSAGE, true),
				complete: () => this.finishReply(reply.id),
			});
	}

	private applyStreamEvent(replyId: number, event: ConversationStreamEvent): void {
		switch (event.type) {
			case "token":
				this.patchMessage(replyId, message => ({ ...message, content: message.content + event.text }));
				break;
			case "complete":
				this.patchMessage(replyId, message => ({
					...message,
					content: event.content !== "" ? event.content : message.content,
				}));
				break;
			case "error":
				this.patchMessage(replyId, message => ({ ...message, content: event.detail, error: true }));
				break;
		}
	}

	private finishReply(replyId: number, fallback = EMPTY_REPLY_MESSAGE, error = false): void {
		this.patchMessage(replyId, message => ({
			...message,
			streaming: false,
			error: message.error || error,
			content: message.content === "" ? fallback : message.content,
		}));
		this.busy.set(false);
		// The turn may have dispensed an item, so re-read stock from the backend.
		this.inventory.reload();
	}

	private patchMessage(id: number, patch: (message: ChatMessage) => ChatMessage): void {
		this.messages.update(messages =>
			messages.map(message => (message.id === id ? patch(message) : message)),
		);
	}

	private createMessage(role: ChatMessage["role"], content: string, streaming = false): ChatMessage {
		return { id: this.nextMessageId++, role, content, streaming, error: false };
	}
}

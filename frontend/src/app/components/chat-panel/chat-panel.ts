import {
	ChangeDetectionStrategy,
	Component,
	ElementRef,
	afterRenderEffect,
	input,
	output,
	viewChild,
} from "@angular/core";

import { ChatMessage } from "../../models/chat-message";
import { ChatComposer } from "../chat-composer/chat-composer";
import { ChatMessageBubble } from "../chat-message/chat-message";

@Component({
	selector: "app-chat-panel",
	imports: [ChatMessageBubble, ChatComposer],
	templateUrl: "./chat-panel.html",
	styleUrl: "./chat-panel.css",
	changeDetection: ChangeDetectionStrategy.OnPush,
})
export class ChatPanel {
	readonly title = input("Vending Machine");
	readonly subtitle = input("Ask for a snack or a recommendation");
	readonly messages = input.required<ChatMessage[]>();
	readonly onlineCount = input.required<number>();
	readonly busy = input(false);
	readonly send = output<string>();

	private readonly log = viewChild.required<ElementRef<HTMLElement>>("log");

	constructor() {
		afterRenderEffect(() => {
			// Reading the messages here makes the effect re-run on every update,
			// including streamed tokens, so the newest text stays in view.
			this.messages();
			const element = this.log().nativeElement;
			element.scrollTop = element.scrollHeight;
		});
	}

	protected onlineLabel(): string {
		const count = this.onlineCount();
		return count === 1 ? "1 slot online" : `${count} slots online`;
	}
}

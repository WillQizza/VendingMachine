import { ChangeDetectionStrategy, Component, computed, input, output, signal } from "@angular/core";

@Component({
	selector: "app-chat-composer",
	templateUrl: "./chat-composer.html",
	styleUrl: "./chat-composer.css",
	changeDetection: ChangeDetectionStrategy.OnPush,
})
export class ChatComposer {
	readonly disabled = input(false);
	readonly placeholder = input("Ask for a snack, a recommendation, or what's in stock!");
	readonly send = output<string>();

	protected readonly draft = signal("");
	protected readonly canSend = computed(() => !this.disabled() && this.draft().trim() !== "");

	protected updateDraft(event: Event): void {
		const target = event.target as HTMLInputElement;
		this.draft.set(target.value);
	}

	protected submit(event: Event): void {
		event.preventDefault();
		if (!this.canSend()) {
			return;
		}
		this.send.emit(this.draft().trim());
		this.draft.set("");
	}
}

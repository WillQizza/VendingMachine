import { CurrencyPipe } from "@angular/common";
import { ChangeDetectionStrategy, Component, computed, input, output } from "@angular/core";

import { Slot, isSoldOut } from "../../models/slot";

@Component({
	selector: "app-slot-card",
	imports: [CurrencyPipe],
	templateUrl: "./slot-card.html",
	styleUrl: "./slot-card.css",
	changeDetection: ChangeDetectionStrategy.OnPush,
	host: {
		"[class.sold-out]": "soldOut()",
	},
})
export class SlotCard {
	readonly slot = input.required<Slot>();
	readonly select = output<Slot>();

	protected readonly soldOut = computed(() => isSoldOut(this.slot()));
	protected readonly stockLabel = computed(() => {
		const slot = this.slot();
		return isSoldOut(slot) ? "Sold out" : `${slot.stock} left`;
	});

	protected choose(): void {
		if (!this.soldOut()) {
			this.select.emit(this.slot());
		}
	}
}

import { ChangeDetectionStrategy, Component, input, output } from "@angular/core";

import { Slot, SlotRow } from "../../models/slot";
import { SlotCard } from "../slot-card/slot-card";

@Component({
	selector: "app-slot-grid",
	imports: [SlotCard],
	templateUrl: "./slot-grid.html",
	styleUrl: "./slot-grid.css",
	changeDetection: ChangeDetectionStrategy.OnPush,
})
export class SlotGrid {
	readonly rows = input.required<SlotRow[]>();
	readonly loading = input(false);
	readonly failed = input(false);
	readonly slotSelected = output<Slot>();
}

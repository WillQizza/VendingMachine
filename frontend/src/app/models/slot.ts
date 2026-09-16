/** One slot of the vending machine. */
export interface Slot {
	slot: string;
	name: string;
	price: number;
	stock: number;
	description: string;
}

/** Slots grouped by shelf row (the letter prefix of the slot code). */
export interface SlotRow {
	row: string;
	slots: Slot[];
}

export function isSoldOut(slot: Slot): boolean {
	return slot.stock <= 0;
}

export function groupSlotsByRow(slots: readonly Slot[]): SlotRow[] {
	const rows = new Map<string, Slot[]>();
	for (const slot of slots) {
		const row = slot.slot.charAt(0).toUpperCase();
		const existing = rows.get(row);
		if (existing === undefined) {
			rows.set(row, [slot]);
		} else {
			existing.push(slot);
		}
	}
	return [...rows.entries()].map(([row, rowSlots]) => ({ row, slots: rowSlots }));
}

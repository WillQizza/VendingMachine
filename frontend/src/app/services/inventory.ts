import { httpResource } from "@angular/common/http";
import { Injectable, PLATFORM_ID, computed, inject } from "@angular/core";
import { isPlatformBrowser } from "@angular/common";

import { Slot, groupSlotsByRow } from "../models/slot";
import { API_BASE_URL } from "./api";


/**
 * Handles Inventory API calls
 */
@Injectable({ providedIn: "root" })
export class InventoryService {
	private readonly baseUrl = inject(API_BASE_URL);
	private readonly isBrowser = isPlatformBrowser(inject(PLATFORM_ID));

	private readonly inventory = httpResource<Slot[]>(
		() => (this.isBrowser ? `${this.baseUrl}/inventory` : undefined),
		{ defaultValue: [] },
	);

	readonly slots = this.inventory.value.asReadonly();
	readonly rows = computed(() => groupSlotsByRow(this.slots()));
	readonly onlineCount = computed(() => this.slots().length);
	readonly loading = this.inventory.isLoading;
	readonly failed = computed(() => this.inventory.error() !== undefined);

	/** Re-reads stock from the backend, e.g. after the agent dispenses an item. */
	reload(): void {
		this.inventory.reload();
	}

	findSlot(code: string): Slot | undefined {
		const normalized = code.trim().toUpperCase();
		return this.slots().find(slot => slot.slot === normalized);
	}
}

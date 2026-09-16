export interface SseEvent {
	event: string;
	data: string;
}


export class SseDecoder {
	private buffer = "";

	push(chunk: string): SseEvent[] {
		this.buffer += chunk;
		const events: SseEvent[] = [];
		let boundary = this.findBoundary();
		while (boundary !== null) {
			const raw = this.buffer.slice(0, boundary.index);
			this.buffer = this.buffer.slice(boundary.index + boundary.length);
			const event = this.parseBlock(raw);
			if (event !== null) {
				events.push(event);
			}
			boundary = this.findBoundary();
		}
		return events;
	}

	/** Parse whatever is left once the stream has ended. */
	flush(): SseEvent[] {
		const rest = this.buffer;
		this.buffer = "";
		if (rest.trim() === "") {
			return [];
		}
		const event = this.parseBlock(rest);
		return event === null ? [] : [event];
	}

	private findBoundary(): { index: number; length: number } | null {
		const match = /\r\n\r\n|\n\n|\r\r/.exec(this.buffer);
		if (match === null) {
			return null;
		}
		return { index: match.index, length: match[0].length };
	}

	private parseBlock(block: string): SseEvent | null {
		let event = "message";
		const data: string[] = [];
		for (const line of block.split(/\r\n|\n|\r/)) {
			if (line === "" || line.startsWith(":")) {
				continue;
			}
			const separator = line.indexOf(":");
			const field = separator === -1 ? line : line.slice(0, separator);
			let value = separator === -1 ? "" : line.slice(separator + 1);
			if (value.startsWith(" ")) {
				value = value.slice(1);
			}
			if (field === "event") {
				event = value;
			} else if (field === "data") {
				data.push(value);
			}
		}
		if (data.length === 0) {
			return null;
		}
		return { event, data: data.join("\n") };
	}
}

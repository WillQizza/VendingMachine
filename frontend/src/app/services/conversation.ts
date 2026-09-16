import { HttpClient, HttpErrorResponse, HttpEvent, HttpEventType } from "@angular/common/http";
import { Injectable, inject } from "@angular/core";
import { Observable, catchError, filter, map, mergeMap, of, switchMap, tap, throwError } from "rxjs";

import { API_BASE_URL } from "./api";
import { SseDecoder, SseEvent } from "./sse-decoder";

interface ConversationCreated {
	conversation_id: string;
}

export type ConversationStreamEvent =
	| { type: "token"; text: string }
	| { type: "complete"; content: string }
	| { type: "error"; detail: string };

/**
 * Handles Conversation API calls.
 */
@Injectable({ providedIn: "root" })
export class ConversationService {
	private readonly http = inject(HttpClient);
	private readonly baseUrl = inject(API_BASE_URL);
	private conversationId: string | null = null;

	sendMessage(content: string): Observable<ConversationStreamEvent> {
		return this.send(content, false);
	}

	private send(content: string, retried: boolean): Observable<ConversationStreamEvent> {
		return this.ensureConversation().pipe(
			switchMap(conversationId => this.streamMessage(conversationId, content)),
			catchError((error: unknown) => {
				// The backend keeps conversations in memory. If it restarted, the
				// stored id is stale: start a fresh conversation and try once more.
				if (!retried && error instanceof HttpErrorResponse && error.status === 404) {
					this.conversationId = null;
					return this.send(content, true);
				}
				return throwError(() => error);
			}),
		);
	}

	private ensureConversation(): Observable<string> {
		if (this.conversationId !== null) {
			return of(this.conversationId);
		}
		return this.http.post<ConversationCreated>(`${this.baseUrl}/conversations`, null).pipe(
			map(created => created.conversation_id),
			tap(conversationId => {
				this.conversationId = conversationId;
			}),
		);
	}

	private streamMessage(conversationId: string, content: string): Observable<ConversationStreamEvent> {
		const decoder = new SseDecoder();
		let consumed = 0;
		const url = `${this.baseUrl}/conversations/${encodeURIComponent(conversationId)}/messages`;

		return this.http
			.post(url, { content }, { observe: "events", responseType: "text", reportProgress: true })
			.pipe(
				mergeMap((event: HttpEvent<string>) => {
					if (event.type === HttpEventType.DownloadProgress) {
						const partial = event.partialText ?? "";
						const chunk = partial.slice(consumed);
						consumed = partial.length;
						return decoder.push(chunk).map(toStreamEvent);
					}
					if (event.type === HttpEventType.Response) {
						const body = event.body ?? "";
						const chunk = body.slice(consumed);
						consumed = body.length;
						return [...decoder.push(chunk), ...decoder.flush()].map(toStreamEvent);
					}
					return [];
				}),
				filter((event): event is ConversationStreamEvent => event !== null),
			);
	}
}

function toStreamEvent(sse: SseEvent): ConversationStreamEvent | null {
	const payload = parseJson(sse.data);
	switch (sse.event) {
		case "token":
			return { type: "token", text: readString(payload, "text") };
		case "complete":
			return { type: "complete", content: readString(payload, "content") };
		case "error":
			return { type: "error", detail: readString(payload, "detail") };
		default:
			return null;
	}
}

function parseJson(text: string): Record<string, unknown> {
	try {
		const value: unknown = JSON.parse(text);
		if (typeof value === "object" && value !== null) {
			return value as Record<string, unknown>;
		}
	} catch {
		// Malformed payloads are treated as empty.
	}
	return {};
}

function readString(payload: Record<string, unknown>, key: string): string {
	const value = payload[key];
	return typeof value === "string" ? value : "";
}

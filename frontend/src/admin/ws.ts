import { apiUrl } from "../env";

// ════════════════════════════════════════════════════════════════════
//  WEBSOCKET QUEUE UPDATES
// ════════════════════════════════════════════════════════════════════

export interface QueueUpdateListener {
  (msg: { type: string; event_id?: number | null }): void;
}

export class QueueWebSocket {
  private ws: WebSocket | null = null;
  private url: string;
  private listeners: Set<QueueUpdateListener> = new Set();
  private reconnectAttempts = 0;
  private maxReconnectAttempts = 10;
  private reconnectDelay = 1000; // ms, exponential backoff

  constructor() {
    const protocol = window.location.protocol === "https:" ? "wss:" : "ws:";
    const host = window.location.host;
    const basePath = apiUrl("/api/admin/queue/ws").replace(
      /^https?:\/\//,
      ""
    );
    this.url = `${protocol}//${basePath}`;
  }

  connect(): Promise<void> {
    return new Promise((resolve, reject) => {
      try {
        this.ws = new WebSocket(this.url);

        this.ws.onopen = () => {
          console.log("[ws] connected to queue updates");
          this.reconnectAttempts = 0;
          resolve();
        };

        this.ws.onmessage = (event) => {
          try {
            const msg = JSON.parse(event.data);
            this.listeners.forEach((listener) => listener(msg));
          } catch (e) {
            console.error("[ws] failed to parse message", e);
          }
        };

        this.ws.onerror = () => {
          console.error("[ws] connection error");
          reject(new Error("WebSocket connection failed"));
        };

        this.ws.onclose = () => {
          console.log("[ws] disconnected");
          this.ws = null;
          this.attemptReconnect();
        };
      } catch (e) {
        reject(e);
      }
    });
  }

  private attemptReconnect(): void {
    if (this.reconnectAttempts >= this.maxReconnectAttempts) {
      console.error("[ws] max reconnect attempts reached");
      return;
    }

    const delay = this.reconnectDelay * Math.pow(2, this.reconnectAttempts);
    this.reconnectAttempts++;
    console.log(`[ws] reconnecting in ${delay}ms...`);

    setTimeout(() => {
      this.connect().catch(() => {
        // attemptReconnect will be called on close
      });
    }, delay);
  }

  disconnect(): void {
    if (this.ws) {
      this.ws.close();
      this.ws = null;
    }
  }

  onUpdate(listener: QueueUpdateListener): () => void {
    this.listeners.add(listener);
    return () => {
      this.listeners.delete(listener);
    };
  }

  isConnected(): boolean {
    return this.ws !== null && this.ws.readyState === WebSocket.OPEN;
  }
}

export const queueWs = new QueueWebSocket();

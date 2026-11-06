"use client";

import { useEffect, useRef, useState, useCallback } from "react";

export interface WsEvent {
  event: string;
  data: any;
}

export const useIncidentsSocket = (onEvent?: (event: WsEvent) => void) => {
  const [isConnected, setIsConnected] = useState(false);
  const socketRef = useRef<WebSocket | null>(null);
  const reconnectTimeoutRef = useRef<NodeJS.Timeout>();

  const connect = useCallback(() => {
    const wsUrl = process.env.NEXT_PUBLIC_WS_URL || "ws://localhost:8000/ws/incidents";
    try {
      const ws = new WebSocket(wsUrl);
      socketRef.current = ws;

      ws.onopen = () => {
        setIsConnected(true);
      };

      ws.onmessage = (e) => {
        try {
          const payload: WsEvent = JSON.parse(e.data);
          if (onEvent) onEvent(payload);
        } catch {
          // ignore non-json keepalives
        }
      };

      ws.onclose = () => {
        setIsConnected(false);
        // Attempt auto-reconnect in 3s
        reconnectTimeoutRef.current = setTimeout(() => {
          connect();
        }, 3000);
      };

      ws.onerror = () => {
        ws.close();
      };
    } catch {
      reconnectTimeoutRef.current = setTimeout(() => {
        connect();
      }, 5000);
    }
  }, [onEvent]);

  useEffect(() => {
    connect();

    // Heartbeat ping every 25s
    const pingInterval = setInterval(() => {
      if (socketRef.current && socketRef.current.readyState === WebSocket.OPEN) {
        socketRef.current.send("ping");
      }
    }, 25000);

    return () => {
      clearInterval(pingInterval);
      if (reconnectTimeoutRef.current) clearTimeout(reconnectTimeoutRef.current);
      if (socketRef.current) socketRef.current.close();
    };
  }, [connect]);

  return { isConnected };
};

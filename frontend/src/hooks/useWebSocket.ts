/**
 * WebSocket Hook
 * --------------
 * Gerçek zamanlı bağlantı yönetimi.
 */

import { useEffect, useRef, useCallback } from 'react';
import { useActivityStore } from '../stores/activityStore';
import { useFocusStore } from '../stores/focusStore';

const WS_URL = 'ws://localhost:8000/ws';

export function useWebSocket() {
  const ws = useRef<WebSocket | null>(null);
  const reconnectTimeout = useRef<NodeJS.Timeout>();
  
  const addActivity = useActivityStore((state) => state.addActivity);
  const updateFocusStats = useFocusStore((state) => state.updateStats);

  const connect = useCallback(() => {
    try {
      ws.current = new WebSocket(WS_URL);

      ws.current.onopen = () => {
        console.log('WebSocket connected');
        
        // Ping interval
        const pingInterval = setInterval(() => {
          if (ws.current?.readyState === WebSocket.OPEN) {
            ws.current.send(JSON.stringify({ type: 'ping' }));
          }
        }, 30000);
        
        ws.current.onclose = () => {
          clearInterval(pingInterval);
        };
      };

      ws.current.onmessage = (event) => {
        try {
          const message = JSON.parse(event.data);
          
          switch (message.type) {
            case 'activity':
              addActivity(message.data);
              break;
              
            case 'focus_update':
              updateFocusStats(message.data);
              break;
              
            case 'distraction_warning':
              // Show notification
              if (window.electronAPI) {
                window.electronAPI.showNotification(
                  '⚠️ Dikkat Dağınıklığı',
                  message.data.message
                );
              }
              break;
              
            case 'pong':
              // Connection alive
              break;
              
            default:
              console.log('Unknown message type:', message.type);
          }
        } catch (error) {
          console.error('WebSocket message error:', error);
        }
      };

      ws.current.onerror = (error) => {
        console.error('WebSocket error:', error);
      };

      ws.current.onclose = () => {
        console.log('WebSocket disconnected, reconnecting...');
        reconnectTimeout.current = setTimeout(connect, 5000);
      };
      
    } catch (error) {
      console.error('WebSocket connection error:', error);
      reconnectTimeout.current = setTimeout(connect, 5000);
    }
  }, [addActivity, updateFocusStats]);

  useEffect(() => {
    connect();

    return () => {
      if (reconnectTimeout.current) {
        clearTimeout(reconnectTimeout.current);
      }
      if (ws.current) {
        ws.current.close();
      }
    };
  }, [connect]);

  return ws.current;
}

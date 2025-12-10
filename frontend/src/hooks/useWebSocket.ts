/**
 * WebSocket Hook
 * --------------
 * Gerçek zamanlı bağlantı yönetimi.
 */

import { useEffect, useRef, useCallback } from 'react';
import { useActivityStore } from '../stores/activityStore';
import { useFocusStore } from '../stores/focusStore';
import { useSystemStore } from '../stores/systemStore';

const WS_URL = 'ws://localhost:8000/ws';

export function useWebSocket() {
  const ws = useRef<WebSocket | null>(null);
  const reconnectTimeout = useRef<NodeJS.Timeout>();
  const pingInterval = useRef<NodeJS.Timeout>();
  
  const addActivity = useActivityStore((state) => state.addActivity);
  const updateFocusStats = useFocusStore((state) => state.updateStats);
  const setDistraction = useFocusStore((state) => state.setDistraction);
  const updateSystemStats = useSystemStore((state) => state.updateStats);
  const setConnected = useSystemStore((state) => state.setConnected);
  const addNotification = useSystemStore((state) => state.addNotification);

  const connect = useCallback(() => {
    try {
      ws.current = new WebSocket(WS_URL);

      ws.current.onopen = () => {
        console.log('✅ WebSocket connected');
        setConnected(true);
        
        // Ping interval - her 30 saniyede bir
        pingInterval.current = setInterval(() => {
          if (ws.current?.readyState === WebSocket.OPEN) {
            ws.current.send(JSON.stringify({ type: 'ping' }));
          }
        }, 30000);
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
              setDistraction(true, message.data.keyword);
              addNotification({
                type: 'warning',
                title: '⚠️ Dikkat Dağınıklığı',
                message: message.data.message,
              });
              // Electron notification
              if (window.electronAPI) {
                window.electronAPI.showNotification(
                  '⚠️ Dikkat Dağınıklığı',
                  message.data.message
                );
              }
              break;
              
            case 'system_stats':
              updateSystemStats(message.data);
              break;
              
            case 'course_detected':
              addNotification({
                type: 'info',
                title: '📚 Yeni Kurs Tespit Edildi',
                message: `${message.data.course_name} - Profilinize eklemek ister misiniz?`,
              });
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
        setConnected(false);
      };

      ws.current.onclose = () => {
        console.log('🔌 WebSocket disconnected, reconnecting in 5s...');
        setConnected(false);
        
        if (pingInterval.current) {
          clearInterval(pingInterval.current);
        }
        
        reconnectTimeout.current = setTimeout(connect, 5000);
      };
      
    } catch (error) {
      console.error('WebSocket connection error:', error);
      setConnected(false);
      reconnectTimeout.current = setTimeout(connect, 5000);
    }
  }, [addActivity, updateFocusStats, setDistraction, updateSystemStats, setConnected, addNotification]);

  useEffect(() => {
    connect();

    return () => {
      if (reconnectTimeout.current) {
        clearTimeout(reconnectTimeout.current);
      }
      if (pingInterval.current) {
        clearInterval(pingInterval.current);
      }
      if (ws.current) {
        ws.current.close();
      }
    };
  }, [connect]);

  const sendMessage = useCallback((type: string, data?: any) => {
    if (ws.current?.readyState === WebSocket.OPEN) {
      ws.current.send(JSON.stringify({ type, data }));
    }
  }, []);

  return { ws: ws.current, sendMessage };
}

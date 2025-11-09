import React, { useEffect, useState } from 'react';

const BASE = ((import.meta as any).env?.VITE_API_BASE as string) || 'http://localhost:8000';

interface Props { variant?: 'floating' | 'inline'; }

const ConnectionStatus: React.FC<Props> = ({ variant = 'floating' }) => {
  const [status, setStatus] = useState<'checking' | 'connected' | 'disconnected' | 'reconnecting'>('checking');
  const [lastCheck, setLastCheck] = useState<Date>(new Date());
  const [consecutiveFailures, setConsecutiveFailures] = useState(0);

  const checkConnection = async () => {
    try {
      const controller = new AbortController();
      const timeout = setTimeout(() => controller.abort(), 8000); // Increased from 3s to 8s
      
      const res = await fetch(`${BASE}/health`, { 
        signal: controller.signal,
        cache: 'no-store'
      });
      
      clearTimeout(timeout);
      if (res.ok) {
        setStatus('connected');
        setConsecutiveFailures(0);
      } else {
        setConsecutiveFailures(prev => prev + 1);
        setStatus(consecutiveFailures >= 2 ? 'disconnected' : 'reconnecting');
      }
      setLastCheck(new Date());
    } catch {
      setConsecutiveFailures(prev => prev + 1);
      // Only show as disconnected after 2 consecutive failures (reduces false alarms during reload)
      setStatus(consecutiveFailures >= 1 ? 'disconnected' : 'reconnecting');
      setLastCheck(new Date());
    }
  };

  useEffect(() => {
    checkConnection();
    const interval = setInterval(checkConnection, 10000); // Check every 10s
    return () => clearInterval(interval);
  }, []);

  // Only hide during initial check
  if (status === 'checking') return null;

  const inline = variant === 'inline';

  return (
    <div
      aria-live="polite"
      aria-label={`Backend status: ${status === 'connected' ? 'connected' : 'disconnected'}`}
      style={{
        position: inline ? 'static' : 'absolute',
        top: inline ? undefined : '0.4rem',
        right: inline ? undefined : '0.5rem',
        padding: inline ? '0.25rem 0.55rem' : '0.35rem 0.6rem',
        borderRadius: inline ? '999px' : '4px',
        fontSize: '0.6rem',
        fontWeight: 600,
        display: 'flex',
        alignItems: 'center',
        gap: '0.4rem',
        backgroundColor: status === 'connected' ? '#10b981' : '#dc3545',
        color: 'white',
        boxShadow: '0 2px 4px rgba(0,0,0,0.12)',
        cursor: 'pointer',
        transition: 'background-color 0.2s, transform 0.2s',
        minWidth: '92px',
        justifyContent: 'center'
      }}
      onClick={checkConnection}
      title={`Backend status: ${status === 'connected' ? 'Connected' : 'Disconnected'}\nLast check: ${lastCheck.toLocaleTimeString()}\nClick to recheck now`}
    >
      <span
        style={{
          width: '6px',
          height: '6px',
          borderRadius: '50%',
          backgroundColor: 'white',
          animation: status === 'connected' ? 'none' : 'pulse 2s ease-in-out infinite',
          flexShrink: 0
        }}
      />
      {status === 'connected' ? 'Connected' : status === 'reconnecting' ? 'Reconnecting...' : 'Offline'}
      <style>{`
        @keyframes pulse {
          0%, 100% { opacity: 1; }
          50% { opacity: 0.5; }
        }
      `}</style>
    </div>
  );
};

export default ConnectionStatus;

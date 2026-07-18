import { useState, useEffect } from 'react';
import { CheckCircle, XCircle, AlertTriangle, Info, X } from 'lucide-react';

export type ToastType = 'success' | 'error' | 'warning' | 'info';

interface Toast {
  id: string;
  type: ToastType;
  title: string;
  message?: string;
  duration?: number;
}

interface ToastProps {
  toast: Toast;
  onClose: (id: string) => void;
}

export function Toast({ toast, onClose }: ToastProps) {
  const [isVisible, setIsVisible] = useState(true);

  useEffect(() => {
    const duration = toast.duration || 5000;
    const timer = setTimeout(() => {
      setIsVisible(false);
      setTimeout(() => onClose(toast.id), 300);
    }, duration);

    return () => clearTimeout(timer);
  }, [toast.id, toast.duration, onClose]);

  const getIcon = () => {
    switch (toast.type) {
      case 'success':
        return CheckCircle;
      case 'error':
        return XCircle;
      case 'warning':
        return AlertTriangle;
      case 'info':
        return Info;
      default:
        return Info;
    }
  };

  const getIconColor = () => {
    switch (toast.type) {
      case 'success':
        return 'text-green-600 bg-green-100';
      case 'error':
        return 'text-red-600 bg-red-100';
      case 'warning':
        return 'text-orange-600 bg-orange-100';
      case 'info':
        return 'text-blue-600 bg-blue-100';
      default:
        return 'text-slate-600 bg-slate-100';
    }
  };

  const getBorderColor = () => {
    switch (toast.type) {
      case 'success':
        return 'border-green-500';
      case 'error':
        return 'border-red-500';
      case 'warning':
        return 'border-orange-500';
      case 'info':
        return 'border-blue-500';
      default:
        return 'border-slate-500';
    }
  };

  const Icon = getIcon();

  return (
    <div
      className={`flex items-start gap-3 p-4 bg-white rounded-lg shadow-lg border-l-4 ${getBorderColor()} transition-all duration-300 ${
        isVisible ? 'opacity-100 translate-x-0' : 'opacity-0 translate-x-full'
      }`}
    >
      <div className={`p-2 rounded-full ${getIconColor()}`}>
        <Icon className="h-5 w-5" />
      </div>
      <div className="flex-1 min-w-0">
        <p className="font-medium text-slate-900">{toast.title}</p>
        {toast.message && <p className="text-sm text-slate-500 mt-1">{toast.message}</p>}
      </div>
      <button
        onClick={() => {
          setIsVisible(false);
          setTimeout(() => onClose(toast.id), 300);
        }}
        className="p-1 hover:bg-slate-100 rounded-full transition-colors"
      >
        <X className="h-4 w-4 text-slate-400" />
      </button>
    </div>
  );
}

interface ToastContainerProps {
  toasts: Toast[];
  onClose: (id: string) => void;
}

export function ToastContainer({ toasts, onClose }: ToastContainerProps) {
  return (
    <div className="fixed top-4 right-4 z-50 flex flex-col gap-2 max-w-sm w-full">
      {toasts.map((toast) => (
        <Toast key={toast.id} toast={toast} onClose={onClose} />
      ))}
    </div>
  );
}

// Toast store for managing toasts globally
interface ToastStore {
  toasts: Toast[];
  addToast: (toast: Omit<Toast, 'id'>) => string;
  removeToast: (id: string) => void;
  clearToasts: () => void;
  subscribe: (listener: (toasts: Toast[]) => void) => () => void;
}

let toastStore: ToastStore | null = null;

export const useToast = () => {
  if (!toastStore) {
    toastStore = createToastStore();
  }
  return toastStore;
};

function createToastStore(): ToastStore {
  const toasts: Toast[] = [];
  const listeners: Set<(toasts: Toast[]) => void> = new Set();

  const notify = () => {
    listeners.forEach((listener) => listener([...toasts]));
  };

  return {
    get toasts() {
      return [...toasts];
    },
    addToast: (toast: Omit<Toast, 'id'>) => {
      const id = Math.random().toString(36).substring(2);
      toasts.push({ ...toast, id });
      notify();
      return id;
    },
    removeToast: (id: string) => {
      const index = toasts.findIndex((t) => t.id === id);
      if (index > -1) {
        toasts.splice(index, 1);
        notify();
      }
    },
    clearToasts: () => {
      toasts.length = 0;
      notify();
    },
    subscribe: (listener: (toasts: Toast[]) => void) => {
      listeners.add(listener);
      return () => listeners.delete(listener);
    },
  };
}

// Convenience functions for common toast types
export const toast = {
  success: (title: string, message?: string, duration?: number) => {
    const store = useToast();
    store.addToast({ type: 'success', title, message, duration });
  },
  error: (title: string, message?: string, duration?: number) => {
    const store = useToast();
    store.addToast({ type: 'error', title, message, duration });
  },
  warning: (title: string, message?: string, duration?: number) => {
    const store = useToast();
    store.addToast({ type: 'warning', title, message, duration });
  },
  info: (title: string, message?: string, duration?: number) => {
    const store = useToast();
    store.addToast({ type: 'info', title, message, duration });
  },
};

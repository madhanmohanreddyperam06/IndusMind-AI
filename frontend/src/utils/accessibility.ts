import { useEffect, useRef } from 'react';

// Hook for managing focus trap in modals
export function useFocusTrap(isActive: boolean) {
  const containerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!isActive || !containerRef.current) return;

    const container = containerRef.current;
    const focusableElements = container.querySelectorAll(
      'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
    );
    const firstElement = focusableElements[0] as HTMLElement;
    const lastElement = focusableElements[focusableElements.length - 1] as HTMLElement;

    const handleTab = (e: KeyboardEvent) => {
      if (e.key !== 'Tab') return;

      if (e.shiftKey) {
        if (document.activeElement === firstElement) {
          lastElement.focus();
          e.preventDefault();
        }
      } else {
        if (document.activeElement === lastElement) {
          firstElement.focus();
          e.preventDefault();
        }
      }
    };

    container.addEventListener('keydown', handleTab);
    firstElement?.focus();

    return () => {
      container.removeEventListener('keydown', handleTab);
    };
  }, [isActive]);

  return containerRef;
}

// Hook for managing keyboard shortcuts
export function useKeyboardShortcuts(
  shortcuts: Record<string, () => void>,
  isActive: boolean = true
) {
  useEffect(() => {
    if (!isActive) return;

    const handleKeyDown = (e: KeyboardEvent) => {
      const key = e.key.toLowerCase();
      const shortcut = shortcuts[key];

      if (shortcut) {
        e.preventDefault();
        shortcut();
      }
    };

    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [shortcuts, isActive]);
}

// Hook for auto-focusing elements
export function useAutoFocus(shouldFocus: boolean = true) {
  const ref = useRef<HTMLElement>(null);

  useEffect(() => {
    if (shouldFocus && ref.current) {
      ref.current.focus();
    }
  }, [shouldFocus]);

  return ref;
}

// ARIA attribute generators
export const aria = {
  // For buttons
  button: (label: string, pressed?: boolean, expanded?: boolean) => ({
    'aria-label': label,
    ...(pressed !== undefined && { 'aria-pressed': pressed }),
    ...(expanded !== undefined && { 'aria-expanded': expanded }),
  }),

  // For modals
  modal: (label: string, labelledBy?: string) => ({
    role: 'dialog' as const,
    'aria-modal': true,
    'aria-label': label,
    ...(labelledBy && { 'aria-labelledby': labelledBy }),
  }),

  // For tabs
  tab: (selected: boolean, controls: string) => ({
    role: 'tab' as const,
    'aria-selected': selected,
    'aria-controls': controls,
    tabIndex: selected ? 0 : -1,
  }),

  // For tab panels
  tabPanel: (labelledBy: string) => ({
    role: 'tabpanel' as const,
    'aria-labelledby': labelledBy,
    tabIndex: 0,
  }),

  // For menus
  menuItem: (label: string) => ({
    role: 'menuitem' as const,
    'aria-label': label,
  }),

  // For alerts
  alert: (live: 'polite' | 'assertive' = 'polite') => ({
    role: 'alert' as const,
    'aria-live': live,
  }),

  // For loading states
  loading: (label: string = 'Loading') => ({
    'aria-busy': true,
    'aria-live': 'polite' as const,
    'aria-label': label,
  }),

  // For progress
  progress: (value: number, max: number = 100, label?: string) => ({
    role: 'progressbar' as const,
    'aria-valuenow': value,
    'aria-valuemin': 0,
    'aria-valuemax': max,
    ...(label && { 'aria-label': label }),
  }),

  // For tooltips
  tooltip: (id: string) => ({
    'aria-describedby': id,
  }),

  // For expandable content
  expandable: (expanded: boolean, controls: string, label: string) => ({
    'aria-expanded': expanded,
    'aria-controls': controls,
    'aria-label': label,
  }),
};

// Screen reader only class utility
export const srOnly = 'sr-only';

// Visually hidden but accessible to screen readers
export const visuallyHidden = {
  className: 'absolute w-px h-px p-0 -m-px overflow-hidden whitespace-nowrap border-0',
};

// Announcer for screen readers
export function useAnnouncer() {
  const announce = (message: string, priority: 'polite' | 'assertive' = 'polite') => {
    const announcer = document.createElement('div');
    announcer.setAttribute('role', 'status');
    announcer.setAttribute('aria-live', priority);
    announcer.setAttribute('aria-atomic', 'true');
    announcer.className = 'sr-only';
    announcer.textContent = message;
    
    document.body.appendChild(announcer);
    
    setTimeout(() => {
      document.body.removeChild(announcer);
    }, 1000);
  };

  return { announce };
}

// Color contrast checker (basic implementation)
export function getContrastColor(hexColor: string): 'black' | 'white' {
  const hex = hexColor.replace('#', '');
  const r = parseInt(hex.substr(0, 2), 16);
  const g = parseInt(hex.substr(2, 2), 16);
  const b = parseInt(hex.substr(4, 2), 16);
  
  const luminance = (0.299 * r + 0.587 * g + 0.114 * b) / 255;
  
  return luminance > 0.5 ? 'black' : 'white';
}

// Check if element is focusable
export function isFocusable(element: HTMLElement): boolean {
  const focusableSelectors = [
    'button',
    '[href]',
    'input',
    'select',
    'textarea',
    '[tabindex]:not([tabindex="-1"])',
    '[contenteditable]',
  ];
  
  return focusableSelectors.some((selector) =>
    element.matches(selector)
  );
}

// Get all focusable elements in a container
export function getFocusableElements(container: HTMLElement): HTMLElement[] {
  const focusableSelectors = [
    'button',
    '[href]',
    'input',
    'select',
    'textarea',
    '[tabindex]:not([tabindex="-1"])',
    '[contenteditable]',
  ];
  
  return Array.from(
    container.querySelectorAll(focusableSelectors.join(','))
  ) as HTMLElement[];
}

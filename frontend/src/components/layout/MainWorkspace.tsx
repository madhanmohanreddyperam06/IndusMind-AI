import { ReactNode } from 'react';
import { useUIStore } from '../../stores';
import { cn } from '../../utils';

interface MainWorkspaceProps {
  children: ReactNode;
}

export function MainWorkspace({ children }: MainWorkspaceProps) {
  const { sidebarOpen } = useUIStore();

  return (
    <main
      className={cn(
        'fixed top-0 right-0 bottom-0 bg-slate-50 dark:bg-slate-900 transition-all duration-300 overflow-auto',
        'md:left-0', // Full width on desktop (no sidebar)
        sidebarOpen ? 'left-0' : 'left-0', // Mobile: full width when sidebar is closed
        // When mobile sidebar is open, content is pushed
        sidebarOpen ? 'md:left-0' : 'md:left-0'
      )}
    >
      <div className="pt-16 md:pt-20 px-4 md:px-6 pb-6">
        <div className="max-w-[1400px] mx-auto">
          {children}
        </div>
      </div>
    </main>
  );
}

import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { Toast, ToastContainer } from '../Toast';

describe('Toast Component', () => {
  beforeEach(() => {
    vi.useFakeTimers();
  });

  afterEach(() => {
    vi.restoreAllMocks();
  });

  it('renders toast with correct content', () => {
    const mockOnClose = vi.fn();
    const toast = {
      id: '1',
      type: 'success' as const,
      title: 'Success',
      message: 'Operation completed',
    };

    render(<Toast toast={toast} onClose={mockOnClose} />);

    expect(screen.getByText('Success')).toBeInTheDocument();
    expect(screen.getByText('Operation completed')).toBeInTheDocument();
  });

  it('calls onClose when close button is clicked', () => {
    const mockOnClose = vi.fn();
    const toast = {
      id: '1',
      type: 'error' as const,
      title: 'Error',
    };

    render(<Toast toast={toast} onClose={mockOnClose} />);

    const closeButton = screen.getByRole('button');
    fireEvent.click(closeButton);

    expect(mockOnClose).toHaveBeenCalledWith('1');
  });

  it('auto-dismisses after duration', async () => {
    const mockOnClose = vi.fn();
    const toast = {
      id: '1',
      type: 'info' as const,
      title: 'Info',
      duration: 1000,
    };

    render(<Toast toast={toast} onClose={mockOnClose} />);

    vi.advanceTimersByTime(1000);
    await waitFor(() => {
      expect(mockOnClose).toHaveBeenCalledWith('1');
    });
  });

  it('renders correct icon based on type', () => {
    const mockOnClose = vi.fn();
    const toast = {
      id: '1',
      type: 'warning' as const,
      title: 'Warning',
    };

    render(<Toast toast={toast} onClose={mockOnClose} />);

    // Check for warning icon presence
    const icon = document.querySelector('svg');
    expect(icon).toBeInTheDocument();
  });
});

describe('ToastContainer Component', () => {
  it('renders multiple toasts', () => {
    const mockOnClose = vi.fn();
    const toasts = [
      { id: '1', type: 'success' as const, title: 'Success 1' },
      { id: '2', type: 'error' as const, title: 'Error 1' },
    ];

    render(<ToastContainer toasts={toasts} onClose={mockOnClose} />);

    expect(screen.getByText('Success 1')).toBeInTheDocument();
    expect(screen.getByText('Error 1')).toBeInTheDocument();
  });

  it('renders empty state when no toasts', () => {
    const mockOnClose = vi.fn();

    render(<ToastContainer toasts={[]} onClose={mockOnClose} />);

    // Container should be present but empty
    const container = document.querySelector('.fixed.top-4.right-4');
    expect(container).toBeInTheDocument();
  });
});

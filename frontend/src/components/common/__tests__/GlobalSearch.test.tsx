import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { describe, it, expect, vi } from 'vitest';
import { GlobalSearch } from '../GlobalSearch';

describe('GlobalSearch Component', () => {
  it('does not render when isOpen is false', () => {
    const { container } = render(<GlobalSearch isOpen={false} onClose={vi.fn()} />);
    expect(container.firstChild).toBeNull();
  });

  it('renders when isOpen is true', () => {
    render(<GlobalSearch isOpen={true} onClose={vi.fn()} />);
    expect(screen.getByPlaceholderText('Search documents, knowledge graph, conversations...')).toBeInTheDocument();
  });

  it('calls onClose when backdrop is clicked', () => {
    const mockOnClose = vi.fn();
    render(<GlobalSearch isOpen={true} onClose={mockOnClose} />);

    const backdrop = document.querySelector('.bg-black\\/50');
    fireEvent.click(backbackdrop!);

    expect(mockOnClose).toHaveBeenCalled();
  });

  it('calls onClose when escape key is pressed', () => {
    const mockOnClose = vi.fn();
    render(<GlobalSearch isOpen={true} onClose={mockOnClose} />);

    fireEvent.keyDown(window, { key: 'Escape' });

    expect(mockOnClose).toHaveBeenCalled();
  });

  it('filters results based on search query', async () => {
    render(<GlobalSearch isOpen={true} onClose={vi.fn()} />);

    const input = screen.getByPlaceholderText('Search documents, knowledge graph, conversations...');
    fireEvent.change(input, { target: { value: 'pump' } });

    await waitFor(() => {
      expect(screen.getByText(/pump/i)).toBeInTheDocument();
    });
  });

  it('shows quick actions when query is empty', () => {
    render(<GlobalSearch isOpen={true} onClose={vi.fn()} />);

    expect(screen.getByText('Quick Actions')).toBeInTheDocument();
    expect(screen.getByText('Upload Document')).toBeInTheDocument();
    expect(screen.getByText('Ask AI Copilot')).toBeInTheDocument();
  });

  it('navigates with keyboard arrow keys', () => {
    render(<GlobalSearch isOpen={true} onClose={vi.fn()} />);

    const input = screen.getByPlaceholderText('Search documents, knowledge graph, conversations...');
    fireEvent.change(input, { target: { value: 'test' } });

    fireEvent.keyDown(window, { key: 'ArrowDown' });
    fireEvent.keyDown(window, { key: 'ArrowUp' });

    // Should not throw errors
  });
});

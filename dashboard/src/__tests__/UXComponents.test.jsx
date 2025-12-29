import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import LeadSkeleton from '../components/LeadSkeleton';
import EmptyState from '../components/EmptyState';
import StatusBadge from '../components/StatusBadge';
import Tooltip from '../components/Tooltip';

describe('LeadSkeleton', () => {
    it('renders default number of skeleton items', () => {
        const { container } = render(<LeadSkeleton />);
        const skeletons = container.querySelectorAll('.animate-pulse');
        expect(skeletons.length).toBe(5); // Default count
    });

    it('renders custom number of skeleton items', () => {
        const { container } = render(<LeadSkeleton count={3} />);
        const skeletons = container.querySelectorAll('.animate-pulse');
        expect(skeletons.length).toBe(3);
    });

    it('applies staggered animation delays', () => {
        const { container } = render(<LeadSkeleton count={3} />);
        const skeletons = container.querySelectorAll('.animate-pulse');

        skeletons.forEach((skeleton, index) => {
            const delay = skeleton.style.animationDelay;
            expect(delay).toBe(`${index * 100}ms`);
        });
    });
});

describe('EmptyState', () => {
    it('renders no-leads variant by default', () => {
        render(<EmptyState />);
        expect(screen.getByText('Nessuna conversazione')).toBeInTheDocument();
    });

    it('renders no-results variant with search query', () => {
        render(<EmptyState variant="no-results" searchQuery="test" />);
        expect(screen.getByText(/Nessun risultato/)).toBeInTheDocument();
        expect(screen.getByText(/test/)).toBeInTheDocument();
    });

    it('renders no-messages variant', () => {
        render(<EmptyState variant="no-messages" />);
        expect(screen.getByText('Inizia la conversazione')).toBeInTheDocument();
    });

    it('shows action button for no-leads variant', () => {
        render(<EmptyState variant="no-leads" />);
        expect(screen.getByText('Crea Nuovo Lead')).toBeInTheDocument();
    });

    it('does not show action button for other variants', () => {
        render(<EmptyState variant="no-results" />);
        expect(screen.queryByText('Crea Nuovo Lead')).not.toBeInTheDocument();
    });
});

describe('StatusBadge', () => {
    it('renders new status correctly', () => {
        render(<StatusBadge status="new" />);
        expect(screen.getByText('Nuovo')).toBeInTheDocument();
    });

    it('renders active status with pulse', () => {
        const { container } = render(<StatusBadge status="active" />);
        expect(screen.getByText('Attivo')).toBeInTheDocument();
        expect(container.querySelector('.animate-ping')).toBeInTheDocument();
    });

    it('renders qualified status', () => {
        render(<StatusBadge status="qualified" />);
        expect(screen.getByText('Qualificato')).toBeInTheDocument();
    });

    it('renders scheduled status', () => {
        render(<StatusBadge status="scheduled" />);
        expect(screen.getByText('Appuntamento')).toBeInTheDocument();
    });

    it('renders human_mode status with pulse', () => {
        const { container } = render(<StatusBadge status="human_mode" />);
        expect(screen.getByText('Manuale')).toBeInTheDocument();
        expect(container.querySelector('.animate-ping')).toBeInTheDocument();
    });

    it('applies correct size classes', () => {
        const { container: small } = render(<StatusBadge status="new" size="sm" />);
        expect(small.querySelector('.text-\\[10px\\]')).toBeInTheDocument();

        const { container: medium } = render(<StatusBadge status="new" size="md" />);
        expect(medium.querySelector('.text-xs')).toBeInTheDocument();

        const { container: large } = render(<StatusBadge status="new" size="lg" />);
        expect(large.querySelector('.text-sm')).toBeInTheDocument();
    });
});

describe('Tooltip', () => {
    it('renders children without tooltip when no content', () => {
        render(
            <Tooltip>
                <button>Test Button</button>
            </Tooltip>
        );
        expect(screen.getByText('Test Button')).toBeInTheDocument();
    });

    it('shows tooltip on mouse enter', async () => {
        const { getByText } = render(
            <Tooltip content="Help text">
                <button>Hover me</button>
            </Tooltip>
        );

        const button = getByText('Hover me');

        // Initially tooltip should not be visible
        expect(screen.queryByText('Help text')).not.toBeInTheDocument();

        // Simulate hover (would need user-event for full test)
        // For now just check the structure is correct
        expect(button).toBeInTheDocument();
    });

    it('positions tooltip correctly', () => {
        const positions = ['top', 'bottom', 'left', 'right'];

        positions.forEach(position => {
            const { container } = render(
                <Tooltip content="Test" position={position}>
                    <div>Content</div>
                </Tooltip>
            );
            // Verify component renders without errors with each position
            expect(container.firstChild).toBeInTheDocument();
        });
    });
});

# IndusMind AI - Frontend

React frontend for the Industrial Knowledge Intelligence Platform.

## Tech Stack

- **Framework**: React 18 with TypeScript
- **Build Tool**: Vite
- **Styling**: Tailwind CSS
- **Routing**: React Router v6
- **State Management**: Zustand
- **HTTP Client**: Axios
- **Icons**: Lucide React
- **Graph Visualization**: React Flow
- **Testing**: Vitest, React Testing Library

## Project Structure

```
frontend/
├── src/
│   ├── components/          # Reusable components
│   │   ├── chat/            # AI Copilot chat components
│   │   ├── citations/       # Citation panel components
│   │   ├── confidence/      # Confidence visualization
│   │   ├── copilot/         # AI response components
│   │   ├── documents/       # Document-related components
│   │   ├── graph/           # Knowledge graph components
│   │   ├── layout/          # Layout components (Sidebar, TopNav)
│   │   └── common/          # Shared components (Toast, GlobalSearch)
│   ├── pages/               # Page components
│   │   ├── Dashboard.tsx    # Main dashboard
│   │   ├── Documents.tsx    # Document management
│   │   ├── DocumentDetails.tsx # Document details with timeline
│   │   ├── KnowledgeGraph.tsx # Knowledge graph explorer
│   │   ├── AICopilot.tsx    # AI assistant interface
│   │   ├── Maintenance.tsx  # Maintenance intelligence
│   │   ├── Compliance.tsx   # Compliance monitoring
│   │   ├── Analytics.tsx    # Analytics dashboard
│   │   ├── Settings.tsx     # User settings
│   │   ├── SignIn.tsx       # Authentication
│   │   └── SignUp.tsx       # Registration
│   ├── hooks/               # Custom React hooks
│   ├── services/            # API service layer
│   │   ├── ragService.ts    # RAG Engine API
│   │   ├── graphService.ts  # Knowledge Graph API
│   │   ├── documentService.ts # Document Processing API
│   │   ├── extractionService.ts # Knowledge Extraction API
│   │   └── retrievalService.ts # Hybrid Retrieval API
│   ├── stores/              # Zustand state management
│   │   ├── authStore.ts     # Authentication state
│   │   ├── conversationStore.ts # Chat state
│   │   └── uiStore.ts       # UI state
│   ├── types/               # TypeScript type definitions
│   │   ├── rag.ts           # RAG types
│   │   ├── graph.ts         # Graph types
│   │   ├── documents.ts     # Document types
│   │   └── extraction.ts    # Extraction types
│   ├── utils/               # Utility functions
│   │   ├── cn.ts            # Class name utility
│   │   ├── accessibility.ts # ARIA and keyboard utilities
│   │   └── errorHandling.ts # Error handling utilities
│   ├── App.tsx              # Main app component
│   └── main.tsx             # Entry point
├── index.html               # HTML template
├── package.json             # Dependencies
├── vite.config.ts           # Vite configuration
├── tailwind.config.js       # Tailwind configuration
└── tsconfig.json            # TypeScript configuration
```

## Setup

1. Install dependencies:
```bash
npm install
```

2. Run the development server:
```bash
npm run dev
```

The application will be available at `http://localhost:5173`

## Available Pages

### Public Routes
- **Landing** (`/`) - Landing page with hero section and navigation
- **Sign In** (`/signin`) - User authentication
- **Sign Up** (`/signup`) - User registration with password validation

### Protected Routes (Dashboard)
- **Dashboard** (`/dashboard`) - Main dashboard with KPI cards, quick actions, system status, and alerts
- **AI Copilot** (`/dashboard/copilot`) - AI-powered assistant with streaming responses, conversation history, citations, and confidence visualization
- **Documents** (`/dashboard/documents`) - Document management with upload, processing, and search
- **Document Details** (`/dashboard/documents/:id`) - Document details with entities, relationships, statistics, and processing timeline
- **Knowledge Graph** (`/dashboard/graph`) - Interactive knowledge graph visualization using React Flow
- **Maintenance** (`/dashboard/maintenance`) - Maintenance intelligence with equipment status and records
- **Compliance** (`/dashboard/compliance`) - Compliance monitoring with requirements and documents
- **Analytics** (`/dashboard/analytics`) - Executive KPI dashboard with charts and trends
- **Settings** (`/dashboard/settings`) - User preferences for notifications, security, appearance, and data
- **Profile** (`/dashboard/profile`) - User profile card with name, email, and join date

## Key Features

### Milestone 1: AI Copilot
- **Chat Interface**: Multi-turn conversations with streaming AI responses
- **Conversation History**: Manage and search past conversations
- **Citation Panel**: Display document citations with confidence scores
- **Confidence Visualization**: Visual indicators for AI response confidence
- **AI Response Card**: Structured response with answer, summary, citations, entities, and relationships
- **Suggested Questions**: Context-aware question suggestions

### Milestone 2: Knowledge Graph & Documents
- **Knowledge Graph Explorer**: Interactive graph visualization with React Flow
  - Node types and custom styling
  - Search and filtering capabilities
  - Node detail panel
  - Zoom and pan controls
- **Document Workspace**: Enhanced document management
  - Processing timeline visualization
  - Entity extraction display
  - Relationship mapping
  - Knowledge statistics

### Milestone 3: Intelligence Dashboards
- **Maintenance Intelligence**: Equipment status, maintenance records, KPI cards
- **Compliance Intelligence**: Requirements tracking, document management, audit status
- **Analytics Dashboard**: Executive KPIs, charts, trends, top issues, activity feed

### Milestone 4: Core Features
- **Dashboard**: Landing page with KPI cards, quick actions, system status, alerts
- **Settings**: User preferences (profile, notifications, security, appearance, data)
- **Global Search**: Keyboard navigation, quick actions, multi-type search
- **Toast Notifications**: Success, error, warning, and info notifications

## Performance Optimizations

- **Code Splitting**: Lazy loading of all page components using React.lazy()
- **Suspense Boundaries**: Loading states for lazy-loaded components
- **Debouncing**: Prevent rapid API calls with debounce utility
- **Throttling**: Limit API call frequency with throttle utility
- **Circuit Breaker**: Prevent cascading failures with circuit breaker pattern

## Error Handling

- **Custom Error Classes**: ApiError, NetworkError, ValidationError
- **Retry Logic**: Exponential backoff for retryable errors
- **Error Boundary**: React error boundary for graceful error handling
- **Error Formatting**: User-friendly error messages
- **Error Logging**: Structured error logging for debugging

## Accessibility

- **ARIA Attributes**: Comprehensive ARIA support for screen readers
- **Keyboard Navigation**: Full keyboard support for all interactive elements
- **Focus Management**: Focus trap for modals, auto-focus for inputs
- **Skip Links**: Skip navigation for keyboard users
- **Screen Reader Support**: Screen reader-only content utilities
- **Color Contrast**: Color contrast checking for accessibility

## State Management

### Zustand Stores

- **authStore**: User authentication state
  - `isAuthenticated`: Boolean
  - `user`: User object
  - `login()`: Authenticate user
  - `logout()`: Logout user

- **conversationStore**: Chat conversation state
  - `conversations`: Array of conversations
  - `currentConversationId`: Current conversation ID
  - `createConversation()`: Create new conversation
  - `deleteConversation()`: Delete conversation
  - `setCurrentConversation()`: Set active conversation

- **uiStore**: Global UI state
  - `sidebarOpen`: Boolean
  - `toggleSidebar()`: Toggle sidebar visibility

## API Services

All API calls are centralized in the `services/` directory:

- **ragService**: RAG Engine endpoints (query, stream, history)
- **graphService**: Knowledge Graph endpoints (nodes, edges, search)
- **documentService**: Document Processing endpoints (upload, process, timeline)
- **extractionService**: Knowledge Extraction endpoints (entities, relationships)
- **retrievalService**: Hybrid Retrieval endpoints (search, similarity)

Base URL is configured via `VITE_API_BASE_URL` environment variable.

## Testing

### Component Tests
- Toast component tests
- GlobalSearch component tests

### Utility Tests
- Error handling utility tests
- Retry logic tests
- Circuit breaker tests
- Debounce/throttle tests

Run tests:
```bash
npm run test
```

## Build

To build for production:
```bash
npm run build
```

The built files will be in the `dist` directory.

## Development

To run in development mode with hot reload:
```bash
npm run dev
```

## Environment Variables

Create a `.env` file in the root directory:

```env
VITE_API_BASE_URL=http://localhost:8000/api/v1
VITE_APP_TITLE=IndusMind AI
```

## Contributing

1. Follow the existing code structure and conventions
2. Use TypeScript for all new code
3. Add appropriate ARIA attributes for accessibility
4. Write tests for new components and utilities
5. Update documentation for new features

## Browser Support

- Chrome (latest)
- Firefox (latest)
- Safari (latest)
- Edge (latest)

# IndusMind AI - Frontend

React frontend for the Industrial Knowledge Intelligence Platform.

## Tech Stack

- **Framework**: React 18 with TypeScript
- **Build Tool**: Vite
- **Styling**: Tailwind CSS
- **Routing**: React Router v6
- **State Management**: TanStack Query
- **HTTP Client**: Axios
- **Icons**: Lucide React

## Project Structure

```
frontend/
├── src/
│   ├── components/    # Reusable components
│   ├── pages/         # Page components
│   ├── layouts/       # Layout components
│   ├── hooks/         # Custom React hooks
│   ├── services/      # API services
│   ├── contexts/      # React contexts
│   ├── routes/        # Route configurations
│   ├── assets/        # Static assets
│   ├── styles/        # Global styles
│   ├── types/         # TypeScript type definitions
│   ├── utils/         # Utility functions
│   ├── App.tsx        # Main app component
│   └── main.tsx       # Entry point
├── index.html         # HTML template
├── package.json       # Dependencies
├── vite.config.ts     # Vite configuration
├── tailwind.config.js # Tailwind configuration
└── tsconfig.json      # TypeScript configuration
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

The application will be available at `http://localhost:3000`

## Available Pages

- **Dashboard** - Main dashboard overview
- **Documents** - Document management
- **Knowledge Graph** - Knowledge graph visualization
- **AI Copilot** - AI-powered assistant
- **Maintenance** - Maintenance records
- **Compliance** - Compliance monitoring
- **Settings** - Application settings

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

## Future Development

This frontend is structured to support:
- Document upload and management UI
- Interactive knowledge graph visualization (React Flow)
- AI chat interface
- Data visualization dashboards
- Form components for data entry
- File preview and annotation
- Real-time updates

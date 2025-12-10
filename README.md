# Anatomy Explorer

Interactive 3D anatomy visualization for education and fitness.

## Overview

Anatomy Explorer is a web-based tool that allows users to explore human anatomy through an interactive 3D model. It supports two view modes:

- **Fitness Mode**: Uses common names and practical descriptions targeted at fitness enthusiasts
- **Clinical Mode**: Uses proper anatomical terminology for medical/educational use

## Features

- 🦴 Interactive 3D anatomy model with hover highlighting
- 🔄 Smooth rotation and zoom controls
- 📚 Dual-audience content (fitness vs clinical terminology)
- 👁️ Layer visibility controls (bones, muscles, tendons, etc.)
- 🔍 Zoom-based layer reveal (deeper structures appear as you zoom in)
- 📋 Detailed info panel with muscle origins, insertions, actions, and exercises

## Tech Stack

- **React 18** with TypeScript
- **Three.js** via react-three-fiber (R3F)
- **@react-three/drei** for 3D helpers
- **Zustand** for state management
- **Tailwind CSS** for styling
- **Vite** for development and builds

## Getting Started

### Prerequisites

- Node.js 18+ 
- npm or yarn

### Installation

```bash
# Clone the repository
git clone <your-repo-url>
cd anatomy-explorer

# Install dependencies
npm install

# Start development server
npm run dev
```

The app will be available at `http://localhost:5173`

### Build for Production

```bash
npm run build
npm run preview
```

## Project Structure

```
anatomy-explorer/
├── public/
│   └── models/          # 3D model files (glTF/glb)
├── src/
│   ├── components/
│   │   ├── layout/      # App layout components
│   │   ├── ui/          # UI overlays (InfoPanel, controls)
│   │   └── viewer/      # 3D viewer components
│   ├── data/            # Anatomy data and content
│   ├── hooks/           # Custom React hooks
│   ├── store/           # Zustand state management
│   ├── types/           # TypeScript type definitions
│   └── utils/           # Utility functions
├── App.tsx
└── main.tsx
```

## Data Model

The application uses a structured data model for anatomical information:

- **AnatomicalStructure**: Core identity (names, type, layer, regions)
- **StructureContent**: Educational content (descriptions, muscle details)
- **RenderConfig**: Visual configuration (colors, opacity, label positions)
- **Region**: Body region hierarchy for navigation

See `src/types/anatomy.ts` for full type definitions.

## Development Roadmap

### Phase 0: Feasibility (Current)
- [x] Project setup with R3F and TypeScript
- [x] Basic scene with placeholder geometry
- [x] Hover highlighting and selection
- [x] Info panel with structure details
- [ ] Load actual 3D model from Z-Anatomy

### Phase 1: Torso MVP
- [ ] Export torso structures from Z-Anatomy (Blender)
- [ ] Implement layer reveal on zoom
- [ ] Add search functionality
- [ ] Complete educational content for all torso structures

### Phase 2: Expansion
- [ ] Additional body regions
- [ ] User accounts and progress tracking
- [ ] Quiz/learning mode
- [ ] Monetization features

## Data Sources

This project uses open-source anatomical data from:

- **Z-Anatomy** (CC BY-SA 4.0) - 3D models derived from BodyParts3D
- **Wikipedia** - Anatomical definitions and descriptions

Attribution: "BodyParts3D - The Database Center for Life Science - CC-BY-SA 2.1 Japan"

## License

MIT

## Contributing

Contributions welcome! Please read the contributing guidelines before submitting PRs.

## Acknowledgments

- Z-Anatomy project for open-source anatomical models
- BodyParts3D for the original dataset
- The react-three-fiber community

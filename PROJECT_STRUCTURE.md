# Nymo Art v4 - Projekt Struktur

## Übersicht
Eine saubere, modulare Anwendung für KI-Bildgenerierung mit Leonardo AI APIs.

## Projektstruktur

```
nymo-art-v4/
├── README.md                    # Hauptdokumentation
├── requirements.txt             # Python-Abhängigkeiten
├── .env.example                 # Umgebungsvariablen-Vorlage
├── .gitignore                   # Git-Ignore-Regeln
├── 
├── scripts/                     # CLI Tools und Utilities
│   ├── generate_test_images.py  # Test-Bildgenerierung Script
│   ├── batch_process.py         # Batch-Verarbeitung CLI Tool
│   └── example_prompts_batch.csv # Beispiel CSV für Batch-Processing
├──
├── backend/                     # Python Backend
│   ├── pyproject.toml          # Python Projekt-Konfiguration
│   ├── app/                    # FastAPI Anwendung
│   │   ├── main.py            # FastAPI App Entry Point
│   │   ├── api/               # API Router
│   │   └── routes/            # API Endpunkte
│   │       ├── generations.py # Bildgenerierung Endpunkte
│   │       ├── models.py      # Modell-Info Endpunkte
│   │       ├── images.py      # Bild-Download Endpunkte
│   │       └── batch.py       # Batch-Processing Endpunkte
│   ├── core/                  # Kernlogik
│   │   ├── schemas.py         # Pydantic Datenmodelle
│   │   ├── batch_processor.py # Batch-Verarbeitung
│   │   └── engine/            # AI Engine Implementierungen
│   │       ├── base.py        # Basis Engine Interface
│   │       └── leonardo/      # Leonardo AI Engines
│   │           ├── phoenix.py    # Phoenix Model Engine
│   │           ├── flux.py       # FLUX Model Engine
│   │           └── photoreal.py  # PhotoReal Engine
│   ├── services/              # Externe Services
│   │   └── leonardo_client.py # Leonardo API Client
│   ├── tests/                 # Tests
│   │   ├── unit/             # Unit Tests
│   │   └── integration/      # Integration Tests
│   └── generated_images/      # Generierte Bilder (Output)
└──
└── frontend/                   # React Frontend
    ├── package.json           # NPM Abhängigkeiten
    ├── vite.config.ts         # Vite Konfiguration
    ├── tsconfig.json          # TypeScript Konfiguration
    ├── tailwind.config.js     # Tailwind CSS Konfiguration
    ├── index.html             # HTML Entry Point
    ├── test-api.html          # API Test Interface
    ├── public/                # Statische Assets
    └── src/                   # React Quellcode
        ├── App.tsx            # Haupt-App Komponente
        ├── main.tsx           # React Entry Point
        ├── theme.ts           # Material-UI Theme
        ├── components/        # Wiederverwendbare Komponenten
        │   ├── Layout.tsx           # App Layout mit Navigation
        │   ├── ModelSelector.tsx    # AI Model Auswahl
        │   ├── PromptInput.tsx      # Prompt Eingabefeld
        │   ├── DimensionsSelector.tsx # Bildgrößen-Auswahl
        │   ├── PhoenixSettings.tsx   # Phoenix Model Einstellungen
        │   ├── FluxSettings.tsx      # FLUX Model Einstellungen
        │   ├── PhotoRealSettings.tsx # PhotoReal Einstellungen
        │   └── ImageGallery.tsx     # Bild-Galerie Komponente
        ├── hooks/             # Custom React Hooks
        │   └── useFormData.ts       # Form State Management
        ├── pages/             # Seiten Komponenten
        │   ├── Generate.tsx         # Bildgenerierung Seite
        │   └── BatchProcess.tsx     # Batch-Verarbeitung Seite
        └── services/          # API Client Services
            ├── phoenixClient.ts     # Phoenix API Client
            ├── fluxClient.ts        # FLUX API Client
            ├── photorealClient.ts   # PhotoReal API Client
            └── batchClient.ts       # Batch API Client
```

## Architektur

### Backend (Python/FastAPI)
- **Modulare Engine-Architektur**: Jedes AI-Modell hat seine eigene Engine-Implementierung
- **Typsichere APIs**: Pydantic Schemas für Validierung und Dokumentation
- **Async/Await**: Vollständig asynchrone Verarbeitung
- **Testbare Struktur**: Unit und Integration Tests

### Frontend (React/TypeScript)
- **Komponentenbasiert**: Kleine, wiederverwendbare React-Komponenten
- **Custom Hooks**: Saubere Trennung von UI und Business Logic
- **Material-UI Design**: Konsistente, moderne Benutzeroberfläche
- **TypeScript**: Typsicherheit im gesamten Frontend

## Verwendete Technologien

### Backend
- **FastAPI**: Moderne Python Web Framework
- **Pydantic**: Datenvalidierung und Settings
- **aiohttp**: Asynchrone HTTP-Clients
- **pytest**: Testing Framework

### Frontend
- **React 18**: UI Framework
- **TypeScript**: Typsichere JavaScript
- **Material-UI (MUI)**: UI Komponenten-Bibliothek
- **Vite**: Build Tool und Dev Server

### AI APIs
- **Leonardo AI**: Phoenix, FLUX und PhotoReal Models
- **Unterstützte Features**: 
  - Verschiedene Styles und Dimensionen
  - Batch-Verarbeitung
  - Bild-Download und -Verwaltung

## Getting Started

1. **Backend Setup**:
   ```bash
   cd backend
   pip install -r ../requirements.txt
   cp ../.env.example ../.env  # Und API-Keys einfügen
   python -m uvicorn app.main:app --reload
   ```

2. **Frontend Setup**:
   ```bash
   cd frontend
   npm install
   npm run dev
   ```

3. **Testing**:
   ```bash
   # Backend Tests
   cd backend && python -m pytest tests/

   # Frontend Build Test
   cd frontend && npm run build
   ```

## Status
✅ **Aufgeräumt und Funktionsfähig** (Mai 2025)
- Alle redundanten und leeren Dateien entfernt
- Modulare, wartbare Codebase
- Vollständig refaktoriert von monolithischer zu modularer Architektur
- Erfolgreiche Build-Tests für Frontend und Backend

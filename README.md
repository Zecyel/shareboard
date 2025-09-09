# Shareboard - Collaborative Document Platform

A real-time collaborative document platform built with Vue3 frontend and FastAPI backend. Users can create, edit, and share documents without requiring login.

## Features

- **Shared Document List**: Browse all documents in a sidebar
- **Monaco Editor**: Full-featured code/text editor with syntax highlighting
- **Real-time Editing**: Create and modify documents instantly
- **No Authentication Required**: Anyone can create and edit documents
- **Markdown Support**: Built-in markdown syntax highlighting
- **Auto-save**: Documents are saved with a simple button click

## Architecture

- **Frontend**: Vue3 + Vite + Monaco Editor
- **Backend**: Python3 + FastAPI
- **Storage**: JSON file-based storage (easily replaceable with database)

## Quick Start

### Prerequisites

- Python 3.8+
- Node.js 16+
- npm or yarn

### Backend Setup

1. Navigate to the backend directory:
```bash
cd backend
```

2. Install Python dependencies:
```bash
pip install -r requirements.txt
```

3. Start the FastAPI server:
```bash
python main.py
```

The backend will be available at `http://localhost:8000`

### Frontend Setup

1. Navigate to the frontend directory:
```bash
cd frontend
```

2. Install Node.js dependencies:
```bash
npm install
```

3. Start the development server:
```bash
npm run dev
```

The frontend will be available at `http://localhost:5173`

## Usage

1. Open your browser to `http://localhost:5173`
2. Click "+ New Document" to create a new document
3. Click on any document in the left panel to edit it
4. Use the Monaco editor to write content (supports markdown)
5. Click "Save" to save your changes
6. Documents are automatically shared with all users

## API Endpoints

The backend provides a RESTful API:

- `GET /api/documents` - List all documents
- `GET /api/documents/{id}` - Get a specific document
- `POST /api/documents` - Create a new document
- `PUT /api/documents/{id}` - Update a document
- `DELETE /api/documents/{id}` - Delete a document

## Project Structure

```
├── backend/
│   ├── main.py              # FastAPI application
│   ├── requirements.txt     # Python dependencies
│   └── documents.json       # Document storage (auto-generated)
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── DocumentList.vue    # Document sidebar
│   │   │   └── MonacoEditor.vue    # Editor component
│   │   ├── services/
│   │   │   └── api.js              # API client
│   │   ├── App.vue                 # Main app component
│   │   └── main.js                 # Vue app entry point
│   ├── package.json
│   └── vite.config.js
└── README.md
```

## Development

### Running in Development Mode

Both backend and frontend support hot-reload for development:

```bash
# Terminal 1 - Backend
cd backend && python main.py

# Terminal 2 - Frontend  
cd frontend && npm run dev
```

### Building for Production

Frontend:
```bash
cd frontend && npm run build
```

The built files will be in `frontend/dist/`

### Future Enhancements

- Database integration (PostgreSQL, MongoDB)
- Real-time collaboration with WebSockets
- User authentication and permissions
- Document versioning
- Export functionality (PDF, HTML, etc.)
- Syntax highlighting for multiple languages
- Document search functionality

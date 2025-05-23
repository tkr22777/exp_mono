# Text Processor React UI

React components for text and audio processing experiments.

## Structure

```
text_processor/
├── dist/               # Compiled JavaScript bundles
│   ├── main-bundle.js     # Text processor bundle
│   └── audio-bundle.js    # Audio processor bundle
├── src/                # React source code
│   ├── components/     # React components
│   │   ├── TextProcessor.jsx     # Main text processor
│   │   ├── AudioProcessor.jsx    # Main audio processor
│   │   ├── AudioRecorder.jsx     # Audio recording component
│   │   ├── TextInput.jsx         # Text input component
│   │   ├── ProcessedResult.jsx   # Result display component
│   │   └── WebSocketResult.jsx   # WebSocket result component
│   ├── index.js        # Text processor entry point
│   └── audio.js        # Audio processor entry point
├── package.json        # NPM dependencies
└── webpack.config.js   # Multi-bundle webpack config
```

## Pages

- `/experiments/text-processor/` - Text input processing
- `/experiments/text-processor/audio` - Audio recording and processing

## Development

### Installation

```bash
npm install
```

### Build for Development

```bash
npm run dev
```

### Build for Production

```bash
npm run build
```

## Integration with Flask

Components are loaded in Flask templates with configuration passed via `window.experimentConfig`. 
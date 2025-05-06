# Text Processor React UI

This directory contains React components for the Text Processor experiment.

## Structure

```
text_processor/
├── dist/               # Compiled JavaScript (created by webpack)
├── src/                # React source code
│   ├── components/     # React components
│   │   ├── TextProcessor.jsx     # Main component
│   │   ├── TextInput.jsx         # Text input component
│   │   └── ProcessedResult.jsx   # Result display component
│   └── index.js        # Entry point
├── package.json        # NPM dependencies
└── webpack.config.js   # Webpack configuration
```

## Development

### Installation

```bash
npm install
```

### Build for Development

```bash
npm run dev
```

This will start webpack in watch mode, which will automatically recompile when files change.

### Build for Production

```bash
npm run build
```

## Integration with Flask

The React components are loaded in the Flask template at `templates/experiments/text_processor/index.html`.

Configuration is passed from Flask to React via the global `window.experimentConfig` object. 
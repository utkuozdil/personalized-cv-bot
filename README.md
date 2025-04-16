# Personalized CV Bot

A serverless application that processes CVs and provides personalized chat interactions.

## Setup

1. Clone the repository:
```bash
git clone https://github.com/yourusername/personalized-cv-bot.git
cd personalized-cv-bot
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
# For development
pip install -r requirements-dev.txt

# For production only
pip install -r requirements.txt
```

4. Set up environment variables:
```bash
cp .env.example .env
# Edit .env with your configuration
```

## Development

1. Run tests:
```bash
python -m pytest tests/ -v
```

2. Run tests with coverage:
```bash
python -m pytest tests/ -v --cov=src --cov-report=term-missing
```

## Deployment

1. Install Serverless Framework:
```bash
npm install -g serverless
```

2. Deploy:
```bash
serverless deploy
```

## Project Structure

```
.
├── src/
│   ├── handlers/         # Lambda function handlers
│   ├── integrations/     # External service integrations
│   ├── services/         # Internal services
│   └── utility/          # Utility functions
├── tests/               # Test files
├── requirements.txt     # Production dependencies
├── requirements-dev.txt # Development dependencies
└── serverless.yml      # Serverless Framework configuration
```

## Contributing

1. Create a new branch for your feature
2. Make your changes
3. Run tests
4. Submit a pull request

## License

MIT


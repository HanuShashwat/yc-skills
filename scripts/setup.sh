#!/bin/bash
set -e

echo "OpenYC Skills - Local Setup"

# 1. Clone (skip if already in repo)
if [ ! -d ".git" ]; then
  git clone https://github.com/yourname/openyc-skills.git
  cd openyc-skills
fi

# 2. Create venv
python3.11 -m venv .venv
source .venv/bin/activate

# 3. Install dependencies
pip install --upgrade pip
pip install -r requirements.txt

# 4. Download embedding model (cached locally)
python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('all-MiniLM-L6-v2')"

# 5. Initialize database
python -m src.cli init-db

# 6. Copy environment template
if [ ! -f ".env" ]; then
  cp .env.example .env
  echo "Created .env from template. Edit it with your API keys."
else
  echo ".env already exists. Skipping copy."
fi

echo ""
echo "Setup complete!"
echo "Next steps:"
echo "  1. Edit .env with your API keys"
echo "  2. Run: python -m src.cli --help"

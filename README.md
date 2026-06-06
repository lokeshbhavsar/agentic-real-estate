# Agentic Real Estate - Housing Price Prediction Agent

An AI-powered agent for real estate operations, property price prediction, and recommendation system using LangChain and Google Generative AI.

## Project Overview

This project implements an intelligent real estate agent that can:
- Predict property prices based on property features
- Recommend properties based on user preferences
- Analyze location details using latitude/longitude
- Perform blockchain-based contract operations (balance checks, token transfers)

## Project Structure

```
├── AGENT/                           # AI Agent implementation
│   ├── agent.py                    # Main agent orchestrator
│   ├── tool.py                     # Agent tools and utilities
│   └── __init__.py
├── House_prediction_model/          # Property price prediction
│   ├── predict.py                  # ML model for price prediction
│   ├── gurgaon.csv                 # Training dataset
│   └── sqft.ipynb                  # Model notebook
├── House_recommendation/            # Property recommendation system
│   ├── recommendationsystem.ipynb   # Recommendation algorithm
│   ├── predicRec.py                # Recommendation logic
│   ├── toolUtil.py                 # Utility functions
│   └── training_index.py           # Index training
├── ContractOperations/              # Blockchain contract operations
│   ├── rw.py                       # Contract read/write operations
│   └── ABI.json                    # Smart contract ABI
├── GEO_SERVICE/                     # Geolocation services
│   └── getInfoByLatLong.py         # Get location info from coordinates
└── generate_demo_pdf.py            # PDF generation utility
```

## Technologies Used

### Core Framework
- **LangChain** - Agent orchestration and tool management
  - `langchain_core.tools` - Tool decorators
  - `langchain_classic.agents` - Agent initialization and types
  - `langchain_classic.memory` - Conversation memory management

### AI Models
- **Google Generative AI (Gemini)** 
  - `langchain_google_genai.ChatGoogleGenerativeAI` - Gemini 3.1 Flash Lite model
  - Temperature: 0 (deterministic responses)

### Machine Learning
- **Scikit-learn** - ML model training and prediction
- **Joblib** - Model serialization and loading
- **Pandas** - Data manipulation and analysis

### Backend & Blockchain
- **Web3.py** - Ethereum blockchain interactions
- **Smart Contracts** - Custom contract operations for token management

### Data & Geolocation
- **Geopy** - Geolocation services (latitude/longitude to location details)

### Utilities
- **Python-dotenv** - Environment variable management
- **ReportLab** - PDF generation

## Prerequisites

- Python 3.8+
- Google API Key (for Gemini models)
- Ethereum wallet addresses (for contract operations)

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd ss
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create a `.env` file with required credentials:
```env
GOOGLE_API_KEY=your_google_api_key
owner_address=your_ethereum_address
zero_address=0x0000000000000000000000000000000000000000
spender_address=your_spender_address
```

## Running the Agent

### Main Agent Application

To start the interactive housing price prediction agent:

```bash
python AGENT/agent.py
```

This will launch an interactive CLI where you can:
- Query property prices
- Get property recommendations
- Ask about location details
- Check token balances and perform transfers

Example queries:
```
you can see the Instructions file in root directory
```

Type `exit` to quit the application.

### Other Components

- **Price Prediction Model**: See `House_prediction_model/sqft.ipynb`
- **Recommendation System**: See `House_recommendation/recommendationsystem.ipynb`
- **PDF Generation**: `python generate_demo_pdf.py`

## Key Features

### 1. **Price Prediction Tool**
- Predicts property prices based on 14 features
- Features: bedrooms, bathrooms, balconies, facing, age, carpet sqft, superbuilt-up sqft, property type, sector, and coordinates

### 2. **Property Recommendation**
- Content-based or collaborative filtering recommendation
- Recommends properties based on user preferences and budget

### 3. **Location Analysis**
- Gets detailed location information from coordinates
- Provides weather, area details, nearby amenities

### 4. **Smart Contract Operations**
- Check token balance
- Query allowances
- Perform token transfers

## Agent Capabilities

The agent uses **ReAct (Reasoning + Acting)** pattern with the following tools:
- `get_balance` - Check token balance
- `get_allowance` - Check token allowance
- `transfer_from` - Transfer tokens
- `predict_property_price` - Predict property prices
- `recommend_property` - Get property recommendations
- `analyze_location` - Analyze location details

## Configuration

- **LLM Model**: Gemini 3.1 Flash Lite
- **Agent Type**: ZERO_SHOT_REACT_DESCRIPTION
- **Memory**: Conversation Buffer Memory (maintains chat history)
- **Error Handling**: Automatic parsing error handling enabled

## Development

### Running Notebooks

```bash
jupyter notebook House_prediction_model/sqft.ipynb
jupyter notebook House_recommendation/recommendationsystem.ipynb
```

### Testing Individual Components

```bash
python -c "from House_prediction_model.predict import predict_from_text; print(predict_from_text('3 bedrooms, 2 bathrooms, 1500 sqft'))"
```

## Requirements

See `requirements.txt` for all dependencies. Key packages:
- langchain
- langchain-google-genai
- google-generativeai
- scikit-learn
- pandas
- joblib
- python-dotenv
- web3
- geopy
- reportlab

## Author

Lokesh's Housing Price Prediction Agent

## Support

For issues or questions, please refer to the project documentation or create an issue in the repository.

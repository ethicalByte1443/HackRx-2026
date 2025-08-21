# 🛡️ Insurance AI Agent

An intelligent full-stack insurance claim decision-making system that combines **FastAPI** backend with **React TypeScript** frontend, powered by **Hugging Face Transformers** and **Gemma LLM**. This AI agent analyzes insurance clauses and customer queries to predict whether a claim should be **Approved** or **Rejected**, along with justification and estimated amounts.

## 🚀 Features

### Backend Features
- ✨ Uses **llama-3.3-70b-versatile** large language model
- 📑 Parses PDF policy documents using `PyMuPDF`
- 🤖 Uses NLP to analyze **user queries** against **insurance clauses**
- 🔍 **FAISS** vector search with **Sentence Transformers** for efficient clause retrieval
- 🔥 Supports both **local inference** and **Hugging Face Inference API** and **Groq API**
- ⚡ Fast API backend with clean REST endpoints

### Frontend Features
- 🎨 Modern React UI built with **TypeScript**, **Tailwind CSS**, and **ShadCN UI**
- 📤 Drag-and-drop PDF upload functionality
- 💬 Interactive query interface for claim analysis
- 📊 Visual display of matched clauses and AI reasoning
- 🎯 Real-time claim decision results with justification

## 🧠 How It Works

1. **PDF Document Upload & Processing**: 
   - Users upload insurance policy documents via the React frontend
   - The backend parses PDFs using `PyMuPDF` and extracts relevant clauses
   - Clauses are indexed using **FAISS** for efficient similarity search

2. **User Query Processing**:
   - Users submit natural language queries like: *"I underwent surgery after 14 months of policy"*
   - The system retrieves the most relevant clauses using vector similarity

3. **AI-Powered Decision Making**:
   - Query and matched clauses are processed by the **llama-3.3-70b-versatile** using Groq
   - The model returns structured JSON output with decision, amount, and justification

4. **Results Display**:
   - Frontend displays the AI decision with matched clauses and reasoning
   - Users can review the complete analysis workflow

## 🛠️ Tech Stack

### Backend
- **FastAPI** - High-performance web framework
- **Hugging Face Transformers** - LLM integration
- **PyMuPDF** - PDF parsing
- **FAISS** - Vector similarity search
- **Sentence Transformers** - Text embeddings
- **Llama-3.3-70B-Versatile** - Language model for reasoning via Groq API
- **Groq** - Ultra-fast LLM inference platform

### Frontend
- **React** with **TypeScript** - Component-based UI
- **Tailwind CSS** - Utility-first styling
- **ShadCN UI** - Modern component library
- **Vite** - Fast build tool

## 📦 Installation & Setup

### Prerequisites
- **Node.js** (v16+) and **npm**
- **Python** (3.8+)
- **Git**

### Backend Setup

1. **Clone the repository**:
```bash
git clone 
cd insurance-ai-agent
```

2. **Install Python dependencies**:
```bash
pip install -r requirements.txt
```

---
```
**********Step 3 & 4 to run Gemma 1B/2B Locally**********
```
---

3. **For GPU users (CUDA 12.1)**:
```bash
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121
```

4. **For CPU-only users**:
```bash
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu
```

5. **Start the FastAPI server**:
```bash
uvicorn main:app --reload
```

The backend will be available at `http://localhost:8000`

### Frontend Setup

1. **Navigate to frontend directory**:
```bash
cd frontend  # or wherever your React app is located
```

2. **Install dependencies**:
```bash
npm install
```

3. **Start the development server**:
```bash
npm run dev
```

The frontend will be available at `http://localhost:8080`

## 📋 Requirements

### Backend Dependencies (`requirements.txt`)
```
fastapi==0.104.1
uvicorn==0.24.0
pydantic==2.5.0
huggingface_hub==0.19.0
transformers==4.35.0
torch==2.1.0
PyMuPDF==1.23.0
sentence-transformers==2.2.2
faiss-cpu==1.7.4
numpy==1.24.0
groq==0.4.1
```

### Frontend Dependencies (included in `package.json`)
- React 18+
- TypeScript
- Tailwind CSS
- ShadCN UI components
- Vite

## 🔗 API Endpoints

### Backend Endpoints

#### `POST /upload-pdf`
Upload and process insurance policy PDF documents.

**Request**: Multipart form data with PDF file
**Response**: Confirmation of successful processing

#### `POST /query` 
Analyze insurance claims against uploaded policies.

**Request**:
```json
{
  "user_query": "I was hospitalized 10 months after starting the policy."
}
```

**Response**:
```json
{
  "result": {
    "decision": "Rejected",
    "amount": "N/A",
    "justification": "Hospitalization occurred before the 12-month waiting period.",
    "matched_clauses": ["Policy allows hospitalization claims only after 12 months..."]
  }
}
```

#### `GET /docs`
Interactive API documentation (Swagger UI)

## 🧪 Example Usage

### Complete Workflow

1. **Upload Policy Document**:
   - Open the React frontend at `http://localhost:8080`
   - Drag and drop your insurance policy PDF
   - Wait for processing confirmation

2. **Submit Claim Query**:
   - Enter your claim details in natural language
   - Example: *"I need surgery coverage after 15 months of active policy"*

3. **Review AI Decision**:
   - See the AI's decision (Approved/Rejected)
   - Review matched policy clauses
   - Read the detailed justification

### API Testing

You can also test the backend directly:

```bash
# Test the API with curl
curl -X POST "http://localhost:8000/query" \
     -H "Content-Type: application/json" \
     -d '{"user_query": "I underwent surgery after 14 months of policy"}'
```

## 📂 Project Structure

```
HackRX/
├── Backend-ai/
│   ├── main.py              # FastAPI application
│   ├── logic.py             # Claim processing logic  
│   ├── requirements.txt     # Python dependencies
│   └── policy_clause.pdf    # Sample policy document
├── Frontend/
│   ├── src/
│   │   ├── components/      # Reusable UI components
│   │   ├── pages/           # Main application pages
│   │   ├── App.tsx          # Root component
│   │   └── main.tsx         # Application entry point
│   ├── package.json         # Node.js dependencies
│   └── tailwind.config.js   # Tailwind configuration
├── README.md                # This file
└── .gitignore              # Git ignore rules
```

## ⚙️ Configuration

### Environment Variables (Optional)

Create a `.env` file in the backend directory:

```env
HUGGINGFACE_TOKEN=
GROQ_API_KEY=
```

### Frontend Configuration

Update API base URL in `src/config.ts` if needed:

```typescript
export const API_BASE_URL = 'http://localhost:8000';
```

## 🚀 Deployment

### Backend Deployment

For production deployment, consider:

1. **Docker containerization**:
```dockerfile
FROM python:3.9
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

2. **Cloud platforms**: Railway, Heroku, AWS, or Google Cloud

### Frontend Deployment

1. **Build for production**:
```bash
npm run build
```

2. **Deploy static files** to Vercel, Netlify, or any static hosting service

## 🧠 Model Information

- **Primary Model**: `google/gemma-1.1-2b` or `google/gemma-1.1-1b`
- **Embeddings**: `sentence-transformers/all-MiniLM-L6-v2`
- **Vector Search**: FAISS with cosine similarity
- **Local Inference**: No internet required for basic functionality
- **Fallback**: Hugging Face Inference API support

## ✅ Roadmap

### Near Term
- [ ] Enhanced PDF parsing for complex documents
- [ ] Multi-language support
- [ ] Improved error handling and validation
- [ ] User authentication system

### Future Features  
- [ ] Multi-agent system for complex claims
- [ ] Integration with external insurance APIs
- [ ] Advanced fraud detection capabilities
- [ ] Mobile application support
- [ ] Real-time collaboration features

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## 🙋♂️ Support

If you encounter any issues or have questions:

1. Check the [Issues](../../issues) page for existing solutions
2. Create a new issue with detailed information
3. Join our [Discussions](../../discussions) for community support

## 🎯 Key Benefits

- **Faster Processing**: Reduce claim processing time from days to minutes[1][6]
- **Improved Accuracy**: AI-powered analysis reduces human error in claim decisions[8][12]
- **Cost Effective**: Automate up to 50% of claims processing tasks[6]
- **Scalable**: Handle increasing claim volumes without proportional staff increases[8]
- **Transparent**: Clear justifications for every AI decision[10]
- **User-Friendly**: Intuitive interface for both technical and non-technical users[2]

**Built with ❤️ for the future of insurance technology**

[1] https://huggingface.co/spaces/anoopreddyyeddula/Automated-Insurance-Claim-Validation-System/tree/main
[2] https://www.kdnuggets.com/a-simple-to-implement-end-to-end-project-with-huggingface
[3] https://huggingface.co/harshita23sh/setfit-model-intent-classification-insurance
[4] https://towardsdatascience.com/building-nlp-powered-applications-with-hugging-face-transformers-9f561effc84f/
[5] https://railway.com/deploy/z52Exi
[6] https://www.lyzr.ai/blog/ai-agents-for-insurance-claims/
[7] https://intellisqr.com/consulting-services/ai-solution-development
[8] https://intellias.com/ai-agents-for-insurance/
[9] https://github.com/Michael95-m/API-for-insurance-claim-model
[10] https://www.domo.com/glossary/insurance-ai-agents
[11] https://5ly.co/blog/ai-tech-stack/
[12] https://www.rapidinnovation.io/post/ai-agents-for-claims-workflow
[13] https://www.damcogroup.com/blogs/ai-agents-in-insurance-intelligent-leap-beyond-traditional-chatbots
[14] https://markovate.com/intelligent-agents-for-insurance/
[15] https://huggingface.co/datasets/OpenLeecher/lmsys_chat_1m_clean/viewer/default/train
[16] https://www.tcs.com/what-we-do/industries/insurance/white-paper/ai-agents-insurance-claims-function
[17] https://developers.cloudflare.com/developer-platform/llms-full.txt
[18] https://huggingface.co/datasets/shalabh05/shalabh_most_updated/viewer
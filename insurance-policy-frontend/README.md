# 📄 Insurance Claim Analyzer UI

This is a frontend built with **React**, **TypeScript**, **Tailwind CSS**, and **ShadCN UI** to upload insurance-related documents (like PDFs), extract relevant clauses, and query them with AI for claim decisions. The backend is powered by **FastAPI** and integrates **Gemma** for LLM-based reasoning.

---

## ⚙️ Tech Stack

- [React](https://reactjs.org/)
- [TypeScript](https://www.typescriptlang.org/)
- [Tailwind CSS](https://tailwindcss.com/)
- [shadcn/ui](https://ui.shadcn.com/)
- [Vite](https://vitejs.dev/) (for bundling)
- [FastAPI](https://fastapi.tiangolo.com/) (for the backend)
- [FAISS + Sentence Transformers + Gemma 2B] (AI vector search + LLM reasoning)

---

## 🚀 Getting Started

### 1. Clone the repository

```bash
git clone https://github.com/your-username/insurance-ui.git
cd insurance-ui
````

### 2. Install dependencies

Make sure you have [Node.js](https://nodejs.org/) and [npm](https://www.npmjs.com/) installed.

```bash
npm install
```

### 3. Run the development server

```bash
npm run dev
```

The app will be available at [http://localhost:8080](http://localhost:8080)

---

## 🌐 API Configuration

Make sure your **FastAPI backend** is running locally on [http://localhost:8000](http://localhost:8000) and supports:

* `POST /upload-pdf` — to upload a PDF file
* `POST /query` — to ask a question based on PDF content

If the API base URL differs, update the endpoints in `src/pages/UploadPage.tsx`.

---

## 📁 Folder Structure

```
src/
├── components/       # Reusable UI components
├── pages/            # Pages like UploadPage
├── App.tsx           # Main routing component
├── main.tsx          # Vite entry point
├── index.css         # Tailwind + base styles
```

---

## 🧠 Sample Flow

1. Upload a PDF document.
2. It gets parsed on the backend with PyMuPDF.
3. Clauses are stored and indexed with FAISS.
4. User submits a query.
5. The top-K similar clauses are retrieved.
6. The Gemma LLM generates a decision/response.
7. The UI displays matched clauses and reasoning.

---

## ✅ To Do

* [ ] Add authentication (optional)
* [ ] Improve PDF highlighting or preview
* [ ] Add theme toggle (light/dark)
* [ ] Add loading spinners and error handling

---

## 📦 Build for Production

```bash
npm run build
```

Output will be in the `dist/` folder.

---

## 📬 Feedback or Issues?

If you run into any issues or have ideas, feel free to open a GitHub issue or reach out.



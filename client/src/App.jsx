import React, { useState } from "react";

function App() {
  const [fileName, setFileName] = useState(null);
  const [response, setResponse] = useState({});

  const handleUpload = async (e) => {
    const file = e.target.files[0];
    if (!file) return;

    const formData = new FormData();
    formData.append("file", file); // This "file" MUST match FastAPI param name

    try {
      const res = await fetch("http://localhost:8000/upload-pdf", {
        method: "POST",
        body: formData,
      });

      if (!res.ok) throw new Error("Upload failed");

      const data = await res.json();
      console.log("✅ Upload success:", data);
      setResponse(data);
      setFileName(data.filename);
    } catch (err) {
      console.error("❌ Upload error:", err);
    }
  };

  return (
    <div className="p-8">
      <h1 className="text-xl font-bold mb-4">PDF Upload</h1>
      <input type="file" accept="application/pdf" onChange={handleUpload} />

      {fileName && <p className="mt-2 text-green-600">Uploaded: {fileName}</p>}

      {Object.keys(response).length > 0 && (
        <div className="mt-6 space-y-4">
          <div className="p-4 bg-green-100 rounded shadow">
            <strong>Message:</strong> {response.message}
          </div>

          <div className="p-4 bg-blue-100 rounded shadow">
            <strong>User Query:</strong> {response.user_query}
          </div>

          <div className="p-4 bg-yellow-100 rounded shadow">
            <strong>Matched Clauses:</strong>
            <ul className="list-disc pl-5 mt-2 space-y-1">
              {response.matched_clauses.map((clause, index) => (
                <li key={index} className="text-sm whitespace-pre-wrap">
                  {clause}
                </li>
              ))}
            </ul>
          </div>

          <div className="p-4 bg-purple-100 rounded shadow">
            <strong>LLM Response:</strong>
            <ul className="mt-2 space-y-1">
              <li>
                <strong>Decision:</strong> {response.LLM_response.decision}
              </li>
              <li>
                <strong>Amount:</strong> {response.LLM_response.amount}
              </li>
              <li>
                <strong>Justification:</strong>{" "}
                <span className="block whitespace-pre-wrap">
                  {response.LLM_response.justification}
                </span>
              </li>
            </ul>
          </div>
        </div>
      )}
    </div>
  );
}

export default App;

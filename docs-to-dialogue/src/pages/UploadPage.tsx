import React, { useState } from "react";
import { motion } from "framer-motion";
import { ArrowLeft, FileText, File, Mail } from "lucide-react";
import { Link, useParams } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import axios from "axios";

const fileTypeConfig = {
  pdf: {
    title: "PDF Document Upload",
    description: "Upload your insurance PDF documents for analysis",
    icon: FileText,
    accept: ".pdf",
    color: "from-red-500/10 to-red-600/10",
  },
  word: {
    title: "Word Document Upload",
    description: "Upload your Word documents and reports",
    icon: File,
    accept: ".doc,.docx",
    color: "from-blue-500/10 to-blue-600/10",
  },
  email: {
    title: "Email Analysis",
    description: "Upload email files for insurance correspondence analysis",
    icon: Mail,
    accept: ".eml,.msg,.txt",
    color: "from-green-500/10 to-green-600/10",
  },
};

export default function UploadPage() {
  const { type } = useParams<{ type: string }>();
  const [fileName, setFileName] = useState("");
  const [response, setResponse] = useState<any>({});
  const [loading, setLoading] = useState(false);

  const config = fileTypeConfig[type as keyof typeof fileTypeConfig];

  if (!config) {
    return (
      <div className="container mx-auto px-4 py-16 text-center">
        <h1 className="text-2xl font-bold mb-4">Invalid upload type</h1>
        <Link to="/">
          <Button>Return Home</Button>
        </Link>
      </div>
    );
  }

  const IconComponent = config.icon;

  const handleUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    setLoading(true);
    setFileName(file.name);

    const formData = new FormData();
    formData.append("file", file);

    try {
      const res = await fetch("http://localhost:8000/upload-pdf", {
        method: "POST",
        body: formData,
      });

      const data = await res.json();
      console.log("Success OK 200");
      console.log(data);
      setResponse(data);
    } catch (err) {
      console.log("Failed");
      console.error("Upload failed:", err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-background via-background to-muted/30">
      <div className="container mx-auto px-4 py-8">
        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
          className="flex items-center justify-between mb-8"
        >
          <Link to="/">
            <Button variant="ghost" className="flex items-center space-x-2">
              <ArrowLeft className="h-4 w-4" />
              <span>Back to Home</span>
            </Button>
          </Link>
        </motion.div>

        {/* Title Section */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.1 }}
          className="text-center mb-12"
        >
          <div className="flex justify-center mb-4">
            <div
              className={`p-4 bg-gradient-to-br ${config.color} rounded-full`}
            >
              <IconComponent className="h-12 w-12 text-primary" />
            </div>
          </div>
          <h1 className="text-4xl font-bold mb-4 gradient-text">
            {config.title}
          </h1>
          <p className="text-xl text-muted-foreground max-w-2xl mx-auto">
            {config.description}
          </p>
        </motion.div>

        {/* File Upload Section */}
        <div className="grid lg:grid-cols-2 gap-8 max-w-7xl mx-auto">
          <motion.div
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.6, delay: 0.2 }}
          >
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center space-x-2">
                  <IconComponent className="h-5 w-5" />
                  <span>Upload Your Document</span>
                </CardTitle>
              </CardHeader>
              <CardContent>
                <input
                  type="file"
                  accept={config.accept}
                  onChange={handleUpload}
                  className="block w-full border p-2 rounded mt-2"
                />
                {fileName && (
                  <p className="mt-2 text-green-600">Uploaded: {fileName}</p>
                )}
              </CardContent>
            </Card>
          </motion.div>

          {/* Analysis Result */}
          <motion.div
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.6, delay: 0.3 }}
          >
            {loading ? (
              <Card>
                <CardContent className="p-6">⏳ Analyzing...</CardContent>
              </Card>
            ) : Object.keys(response).length > 0 ? (
              <Card className="bg-[#1f1f1f] text-white border border-gray-700 shadow-lg">
                <CardContent className="space-y-4 p-6">
                  <div className="p-4 bg-[#243c2e] rounded shadow-md">
                    <strong className="text-green-300">Message:</strong>{" "}
                    {response.message}
                  </div>

                  <div className="p-4 bg-[#1e3a5f] rounded shadow-md">
                    <strong className="text-blue-300">User Query:</strong>{" "}
                    {response.user_query}
                  </div>

                  <div className="p-4 bg-[#5c4b1f] rounded shadow-md">
                    <strong className="text-yellow-300">
                      Matched Clauses:
                    </strong>
                    <ul className="list-disc pl-5 mt-2 space-y-1 text-sm text-white">
                      {response.matched_clauses?.map(
                        (clause: string, index: number) => (
                          <li key={index} className="whitespace-pre-wrap">
                            {clause}
                          </li>
                        )
                      )}
                    </ul>
                  </div>

                  <div className="p-4 bg-[#3f2a52] rounded shadow-md">
                    <strong className="text-purple-300">LLM Response:</strong>
                    <ul className="mt-2 space-y-1">
                      <li>
                        <strong className="text-purple-200">Decision:</strong>{" "}
                        {response.LLM_response?.decision}
                      </li>
                      <li>
                        <strong className="text-purple-200">Amount:</strong>{" "}
                        {response.LLM_response?.amount}
                      </li>
                      <li>
                        <strong className="text-purple-200">
                          Justification:
                        </strong>
                        <span className="block whitespace-pre-wrap">
                          {response.LLM_response?.justification}
                        </span>
                      </li>
                    </ul>
                  </div>
                </CardContent>
              </Card>
            ) : null}
          </motion.div>
        </div>

        {/* Tips Section */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.4 }}
          className="mt-12 max-w-4xl mx-auto"
        >
          <Card className="bg-gradient-to-r from-primary/5 to-secondary/5">
            <CardContent className="p-6">
              <h3 className="text-lg font-semibold mb-3">
                💡 Tips for better analysis:
              </h3>
              <ul className="space-y-2 text-sm text-muted-foreground">
                <li>• Ensure your document is clear and readable</li>
                <li>• Include all relevant pages and sections</li>
                <li>
                  • Ask specific questions about coverage, deductibles, or claim
                  procedures
                </li>
                <li>• Mention any deadlines or time-sensitive requirements</li>
              </ul>
            </CardContent>
          </Card>
        </motion.div>
      </div>
    </div>
  );
}

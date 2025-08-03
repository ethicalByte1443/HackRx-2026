import { useState, useCallback } from 'react';
import { motion } from 'framer-motion';
import { Upload, File, X } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { cn } from '@/lib/utils';

interface FileUploadProps {
  onFileSelect: (file: File) => void;
  accept?: string;
  className?: string;
}

export function FileUpload({ onFileSelect, accept, className }: FileUploadProps) {
  const [isDragOver, setIsDragOver] = useState(false);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragOver(false);
    
    const files = e.dataTransfer.files;
    if (files.length > 0) {
      const file = files[0];
      setSelectedFile(file);
      onFileSelect(file);
    }
  }, [onFileSelect]);

  const handleDragOver = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragOver(true);
  }, []);

  const handleDragLeave = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragOver(false);
  }, []);

  const handleFileInput = useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
    const files = e.target.files;
    if (files && files.length > 0) {
      const file = files[0];
      setSelectedFile(file);
      onFileSelect(file);
    }
  }, [onFileSelect]);

  const removeFile = () => {
    setSelectedFile(null);
  };

  return (
    <div className={cn("w-full", className)}>
      {!selectedFile ? (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className={cn(
            "upload-area rounded-lg p-8 text-center cursor-pointer transition-all duration-300",
            isDragOver && "dragover"
          )}
          onDrop={handleDrop}
          onDragOver={handleDragOver}
          onDragLeave={handleDragLeave}
          onClick={() => document.getElementById('file-input')?.click()}
        >
          <Upload className="mx-auto h-12 w-12 text-muted-foreground mb-4" />
          <p className="text-lg font-medium mb-2">
            Drop your file here or click to browse
          </p>
          <p className="text-sm text-muted-foreground">
            Supports PDF, Word documents, and email files
          </p>
          <input
            id="file-input"
            type="file"
            accept={accept}
            onChange={handleFileInput}
            className="hidden"
          />
        </motion.div>
      ) : (
        <motion.div
          initial={{ opacity: 0, scale: 0.95 }}
          animate={{ opacity: 1, scale: 1 }}
          className="bg-card border rounded-lg p-4 flex items-center justify-between"
        >
          <div className="flex items-center space-x-3">
            <File className="h-8 w-8 text-primary" />
            <div>
              <p className="font-medium">{selectedFile.name}</p>
              <p className="text-sm text-muted-foreground">
                {(selectedFile.size / 1024 / 1024).toFixed(2)} MB
              </p>
            </div>
          </div>
          <Button
            variant="ghost"
            size="icon"
            onClick={removeFile}
            className="h-8 w-8"
          >
            <X className="h-4 w-4" />
          </Button>
        </motion.div>
      )}
    </div>
  );
}
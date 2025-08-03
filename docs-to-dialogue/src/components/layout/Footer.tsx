import { motion } from 'framer-motion';
import { Github, Heart } from 'lucide-react';

export function Footer() {
  return (
    <motion.footer
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      transition={{ delay: 0.5 }}
      className="mt-auto border-t bg-background/95 backdrop-blur"
    >
      <div className="container flex h-16 items-center justify-center px-4 sm:px-6 lg:px-8">
        <div className="flex items-center space-x-4 text-sm text-muted-foreground">
          <span>Built by</span>
          <i>{"{Team : Aseem, Divyansh, Deepali, Ashwika}"}</i>
          <span>for HackRX 2025</span>
          <a
            href="https://github.com"
            target="_blank"
            rel="noopener noreferrer"
            className="inline-flex items-center space-x-1 hover:text-foreground transition-colors"
          >
            <Github className="h-4 w-4" />
            <span>GitHub</span>
          </a>
        </div>
      </div>
    </motion.footer>
  );
}
import { motion } from 'framer-motion';
import { FileText, File, Mail, Shield, CheckCircle, Clock, Users } from 'lucide-react';
import { Link } from 'react-router-dom';
import { Button } from '@/components/ui/button';
import { Card, CardContent } from '@/components/ui/card';

const Index = () => {
  const fileTypes = [
    {
      id: 'pdf',
      title: 'Upload PDF',
      description: 'Submit insurance documents, policies, and claim forms in PDF format',
      icon: FileText,
      color: 'from-red-500/20 to-red-600/20',
      hoverColor: 'hover:from-red-500/30 hover:to-red-600/30',
      path: '/upload/pdf'
    },
    {
      id: 'word',
      title: 'Upload Word Doc',
      description: 'Upload Word documents, reports, and insurance correspondence',
      icon: File,
      color: 'from-blue-500/20 to-blue-600/20',
      hoverColor: 'hover:from-blue-500/30 hover:to-blue-600/30',
      path: '/upload/word'
    },
    {
      id: 'email',
      title: 'Analyze Email',
      description: 'Upload email conversations with insurance companies',
      icon: Mail,
      color: 'from-green-500/20 to-green-600/20',
      hoverColor: 'hover:from-green-500/30 hover:to-green-600/30',
      path: '/upload/email'
    }
  ];

  const features = [
    {
      icon: CheckCircle,
      title: 'Accurate Analysis',
      description: 'AI-powered document analysis for precise claim insights'
    },
    {
      icon: Clock,
      title: 'Fast Processing',
      description: 'Get instant feedback and recommendations on your claims'
    },
    {
      icon: Users,
      title: 'Expert Guidance',
      description: 'Professional advice based on insurance industry standards'
    }
  ];

  return (
    <div className="min-h-screen bg-gradient-to-br from-background via-background to-muted/30">
      {/* Hero Section */}
      <div className="container mx-auto px-4 py-16 sm:py-24">
        <motion.div
          initial={{ opacity: 0, y: 30 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
          className="text-center mb-16"
        >
          <motion.div
            initial={{ scale: 0.9 }}
            animate={{ scale: 1 }}
            transition={{ duration: 0.5, delay: 0.2 }}
            className="flex justify-center mb-6"
          >
            <div className="p-4 bg-gradient-to-br from-primary/20 to-secondary/20 rounded-full">
              <Shield className="h-16 w-16 text-primary animate-float" />
            </div>
          </motion.div>
          
          <h1 className="text-4xl sm:text-5xl lg:text-6xl font-bold mb-6">
            <span className="gradient-text">Insurance Claim</span>
            <br />
            <span className="text-foreground">Assistant</span>
          </h1>
          
          <motion.p
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.4, duration: 0.6 }}
            className="text-xl text-muted-foreground max-w-2xl mx-auto mb-8"
          >
            Upload your insurance documents and get instant, intelligent analysis 
            to help maximize your claim success. Fast, secure, and reliable.
          </motion.p>
        </motion.div>

        {/* File Type Cards */}
        <motion.div
          initial={{ opacity: 0, y: 40 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.3 }}
          className="grid md:grid-cols-3 gap-6 mb-20"
        >
          {fileTypes.map((type, index) => (
            <motion.div
              key={type.id}
              initial={{ opacity: 0, y: 40 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5, delay: 0.1 * index }}
              whileHover={{ scale: 1.02, y: -5 }}
              whileTap={{ scale: 0.98 }}
            >
              <Link to={type.path}>
                <Card className={`hero-card h-full cursor-pointer bg-gradient-to-br ${type.color} ${type.hoverColor} transition-all duration-300`}>
                  <CardContent className="p-8 text-center">
                    <motion.div
                      whileHover={{ rotate: 5, scale: 1.1 }}
                      transition={{ type: "spring", stiffness: 300 }}
                      className="flex justify-center mb-6"
                    >
                      <div className="p-4 bg-white/50 dark:bg-black/20 rounded-full">
                        <type.icon className="h-12 w-12 text-primary" />
                      </div>
                    </motion.div>
                    
                    <h3 className="text-2xl font-bold mb-3 text-foreground">
                      {type.title}
                    </h3>
                    
                    <p className="text-muted-foreground mb-6">
                      {type.description}
                    </p>
                    
                    <Button className="w-full" size="lg">
                      Get Started
                    </Button>
                  </CardContent>
                </Card>
              </Link>
            </motion.div>
          ))}
        </motion.div>

        {/* Features Section */}
        <motion.div
          initial={{ opacity: 0, y: 40 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.6 }}
          className="text-center"
        >
          <h2 className="text-3xl font-bold mb-12 text-foreground">
            Why Choose ClaimAssist?
          </h2>
          
          <div className="grid md:grid-cols-3 gap-8">
            {features.map((feature, index) => (
              <motion.div
                key={index}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.5, delay: 0.7 + index * 0.1 }}
                className="text-center"
              >
                <motion.div
                  whileHover={{ scale: 1.1, rotate: 5 }}
                  className="inline-flex items-center justify-center w-16 h-16 bg-primary/10 rounded-full mb-4"
                >
                  <feature.icon className="h-8 w-8 text-primary" />
                </motion.div>
                <h3 className="text-xl font-semibold mb-2">{feature.title}</h3>
                <p className="text-muted-foreground">{feature.description}</p>
              </motion.div>
            ))}
          </div>
        </motion.div>
      </div>
    </div>
  );
};

export default Index;

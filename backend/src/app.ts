import express from 'express';
import cors from 'cors';
import helmet from 'helmet';
import compression from 'compression';
import { config } from '@/core/config';


const app = express();

// Security middleware
app.use(helmet());

// CORS middleware
app.use(cors({
  origin: config.cors.origin,
  credentials: true,
}));

// Body parsing middleware
app.use(express.json({ limit: '10mb' }));
app.use(express.urlencoded({ extended: true, limit: '10mb' }));

// Compression middleware
app.use(compression());

// Health check endpoint
app.get('/health', (req, res) => {
  res.status(200).json({
    status: 'ok',
    timestamp: new Date().toISOString(),
    service: 'pulse-ops-backend',
    version: '1.0.0',
  });
});

// API routes will be mounted here
// app.use('/api/v1', routes);

// Global error handler will be added here

const PORT = config.server.port || 3000;

if (require.main === module) {
  app.listen(PORT, () => {
    
  });
}

export default app;

const express = require('express');
const cors = require('cors');
const compression = require('compression');
const helmet = require('helmet');
const rateLimit = require('express-rate-limit');
const path = require('path');
const fs = require('fs-extra');
const { program } = require('commander');

const WorkflowDatabase = require('./database');

// Initialize Express app
const app = express();
const db = new WorkflowDatabase();

// Security middleware
app.use(helmet({
  contentSecurityPolicy: {
    directives: {
      defaultSrc: ["'self'"],
      styleSrc: ["'self'", "'unsafe-inline'", "https://cdn.jsdelivr.net"],
      scriptSrc: ["'self'", "'unsafe-inline'", "https://cdn.jsdelivr.net"],
      imgSrc: ["'self'", "data:", "https:"],
      connectSrc: ["'self'"],
      fontSrc: ["'self'", "https://fonts.gstatic.com"],
      objectSrc: ["'none'"],
      mediaSrc: ["'self'"],
      frameSrc: ["'none'"],
    },
  },
}));

// Rate limiting
const limiter = rateLimit({
  windowMs: 15 * 60 * 1000, // 15 minutes
  max: 1000, // limit each IP to 1000 requests per windowMs
  message: 'Too many requests from this IP, please try again later.'
});
app.use('/api/', limiter);

// Middleware
app.use(compression());
app.use(cors());
app.use(express.json());
app.use(express.urlencoded({ extended: true }));

// Serve static files
app.use(express.static(path.join(__dirname, '../static')));

// Health check endpoint
app.get('/health', (req, res) => {
  res.json({ status: 'healthy', message: 'N8N Workflow API is running' });
});

// Main page
app.get('/', (req, res) => {
  const staticPath = path.join(__dirname, '../static/index.html');
  
  if (fs.existsSync(staticPath)) {
    res.sendFile(staticPath);
  } else {
    res.status(404).send(`
      <html><body>
        <h1>Setup Required</h1>
        <p>Static files not found. Please ensure the static directory exists with index.html</p>
        <p>Current directory: ${process.cwd()}</p>
      </body></html>
    `);
  }
});

// API Routes

// Get workflow statistics
app.get('/api/stats', async (req, res) => {
  try {
    const stats = await db.getStats();
    res.json(stats);
  } catch (error) {
    console.error('Error fetching stats:', error);
    res.status(500).json({ error: 'Error fetching stats', details: error.message });
  }
});

// Categories list compatible with static UI (returns {categories: []})
app.get('/api/categories', async (req, res) => {
  try {
    await db.initialize();
    // Use distinct folders as categories fallback
    const sqlite3 = require('sqlite3').verbose();
    const sqliteDb = new sqlite3.Database(db.dbPath);
    sqliteDb.all('SELECT DISTINCT folder FROM workflows WHERE folder IS NOT NULL AND folder != ""', (err, rows) => {
      sqliteDb.close();
      if (err) {
        console.error('Error loading categories:', err);
        return res.json({ categories: ['Uncategorized'] });
      }
      const categories = rows.map(r => r.folder).filter(Boolean).sort();
      res.json({ categories: categories.length ? categories : ['Uncategorized'] });
    });
  } catch (error) {
    console.error('Error fetching categories:', error);
    res.status(500).json({ categories: ['Uncategorized'] });
  }
});

// Filename -> category mappings (returns {mappings: {filename: category}})
app.get('/api/category-mappings', async (req, res) => {
  try {
    await db.initialize();
    const sqlite3 = require('sqlite3').verbose();
    const sqliteDb = new sqlite3.Database(db.dbPath);
    sqliteDb.all('SELECT filename, COALESCE(NULLIF(folder, ""), "Uncategorized") AS category FROM workflows', (err, rows) => {
      sqliteDb.close();
      if (err) {
        console.error('Error loading category mappings:', err);
        return res.json({ mappings: {} });
      }
      const mappings = {};
      rows.forEach(r => { mappings[r.filename] = r.category || 'Uncategorized'; });
      res.json({ mappings });
    });
  } catch (error) {
    console.error('Error fetching category mappings:', error);
    res.status(500).json({ mappings: {} });
  }
});

// Search workflows
app.get('/api/workflows', async (req, res) => {
  try {
    const {
      q = '',
      trigger = 'all',
      complexity = 'all',
      active_only = false,
      page = 1,
      per_page = 20,
      exclude_legacy = 'false', // when true, hides files with numeric prefix (legacy set)
      new_only = 'false',
    } = req.query;
    
    const pageNum = Math.max(1, parseInt(page));
    const perPage = Math.min(100, Math.max(1, parseInt(per_page)));
    const offset = (pageNum - 1) * perPage;
    const activeOnly = active_only === 'true';
    
    const { workflows, total } = await db.searchWorkflows(
      q, trigger, complexity, activeOnly, perPage, offset
    );
    // Optional filter to exclude legacy files (numeric prefix like 0001_)
    const wantNewOnly = (exclude_legacy === 'true') || (new_only === 'true') || (exclude_legacy === '1') || (new_only === '1');
    const filtered = wantNewOnly
      ? workflows.filter(w => !/^\d+_/.test(w.filename))
      : workflows;

    const filteredTotal = wantNewOnly ? filtered.length + (total - workflows.length) : total;
    const pages = Math.ceil(filteredTotal / perPage);

    res.json({
      workflows: filtered,
      total: filteredTotal,
      page: pageNum,
      per_page: perPage,
      pages,
      query: q,
      filters: {
        trigger,
        complexity,
        active_only: activeOnly
      }
    });
  } catch (error) {
    console.error('Error searching workflows:', error);
    res.status(500).json({ error: 'Error searching workflows', details: error.message });
  }
});

// Get workflow detail
app.get('/api/workflows/:filename', async (req, res) => {
  try {
    const { filename } = req.params;
    const workflow = await db.getWorkflowDetail(filename);

    if (!workflow) {
      return res.status(404).json({ error: 'Workflow not found' });
    }

    // Normalize response to match frontend expectation (raw_json)
    const metadata = {
      id: workflow.id,
      filename: workflow.filename,
      name: workflow.name,
      folder: workflow.folder,
      active: !!workflow.active,
      description: workflow.description || '',
      trigger_type: workflow.trigger_type,
      complexity: workflow.complexity,
      node_count: workflow.node_count,
      integrations: workflow.integrations || [],
      tags: workflow.tags || [],
      created_at: workflow.created_at,
      updated_at: workflow.updated_at,
    };

    res.json({
      // Keep original for compatibility
      ...workflow,
      metadata,
      raw_json: workflow.raw_workflow || null,
    });
  } catch (error) {
    console.error('Error fetching workflow detail:', error);
    res.status(500).json({ error: 'Error fetching workflow detail', details: error.message });
  }
});

// Download workflow
app.get('/api/workflows/:filename/download', async (req, res) => {
  try {
    const { filename } = req.params;

    // Try to resolve using DB (has folder info)
    const workflow = await db.getWorkflowDetail(filename);
    let candidatePath = workflow && workflow.folder
      ? path.join('workflows', workflow.folder, filename)
      : path.join('workflows', filename);

    if (!fs.existsSync(candidatePath)) {
      // Fallback: search recursively by filename
      const stack = ['workflows'];
      let found = null;
      while (stack.length && !found) {
        const current = stack.pop();
        const entries = fs.readdirSync(current, { withFileTypes: true });
        for (const entry of entries) {
          const full = path.join(current, entry.name);
          if (entry.isDirectory()) {
            stack.push(full);
          } else if (entry.isFile() && path.basename(full) === filename) {
            found = full;
            break;
          }
        }
      }
      if (found) candidatePath = found;
    }

    if (!fs.existsSync(candidatePath)) {
      return res.status(404).json({ error: 'Workflow file not found' });
    }

    res.setHeader('Content-Disposition', `attachment; filename="${filename}"`);
    res.setHeader('Content-Type', 'application/json; charset=utf-8');
    res.sendFile(path.resolve(candidatePath));
  } catch (error) {
    console.error('Error downloading workflow:', error);
    res.status(500).json({ error: 'Error downloading workflow', details: error.message });
  }
});

// Get workflow diagram (Mermaid)
app.get('/api/workflows/:filename/diagram', async (req, res) => {
  try {
    const { filename } = req.params;
    const workflow = await db.getWorkflowDetail(filename);
    
    if (!workflow || !workflow.raw_workflow) {
      return res.status(404).json({ error: 'Workflow not found' });
    }
    
    const diagram = generateMermaidDiagram(workflow.raw_workflow.nodes, workflow.raw_workflow.connections);
    res.json({ diagram });
  } catch (error) {
    console.error('Error generating diagram:', error);
    res.status(500).json({ error: 'Error generating diagram', details: error.message });
  }
});

// Generate Mermaid diagram
function generateMermaidDiagram(nodes, connections) {
  if (!nodes || nodes.length === 0) {
    return 'graph TD\n    A[No nodes found]';
  }
  
  let diagram = 'graph TD\n';
  
  // Add nodes
  nodes.forEach(node => {
    const nodeId = sanitizeNodeId(node.name);
    const nodeType = node.type?.split('.').pop() || 'unknown';
    diagram += `    ${nodeId}["${node.name}\\n(${nodeType})"]\n`;
  });
  
  // Add connections
  if (connections) {
    Object.entries(connections).forEach(([sourceNode, outputs]) => {
      const sourceId = sanitizeNodeId(sourceNode);
      
      outputs.main?.forEach(outputConnections => {
        outputConnections.forEach(connection => {
          const targetId = sanitizeNodeId(connection.node);
          diagram += `    ${sourceId} --> ${targetId}\n`;
        });
      });
    });
  }
  
  return diagram;
}

function sanitizeNodeId(nodeName) {
  // Convert node name to valid Mermaid ID
  return nodeName.replace(/[^a-zA-Z0-9]/g, '_').replace(/^_+|_+$/g, '');
}

// Reindex workflows
app.post('/api/reindex', async (req, res) => {
  try {
    const { force = false } = req.body;
    
    // Run indexing in background
    db.cleanupMissingFiles()
      .then(() => db.indexWorkflows(force))
      .then(results => {
      console.log('Indexing completed:', results);
    }).catch(error => {
      console.error('Indexing error:', error);
    });
    
    res.json({ message: 'Indexing started in background' });
  } catch (error) {
    console.error('Error starting reindex:', error);
    res.status(500).json({ error: 'Error starting reindex', details: error.message });
  }
});

// AI-friendly endpoints (stable dataset for ingestion)
app.get('/api/ai/workflows', async (req, res) => {
  try {
    const page = Math.max(1, parseInt(req.query.page || '1'));
    const perPage = Math.min(200, Math.max(1, parseInt(req.query.per_page || '50')));
    await db.initialize();
    const all = await db.getAllWorkflowsBasic();
    const total = all.length;
    const start = (page - 1) * perPage;
    const slice = all.slice(start, start + perPage).map(w => ({
      filename: w.filename,
      name: w.name,
      category: w.folder || 'Uncategorized',
      node_count: w.node_count,
      trigger_type: w.trigger_type,
      complexity: w.complexity,
      integrations: w.integrations,
      tags: w.tags,
      active: !!w.active,
      updated_at: w.updated_at,
    }));
    res.json({
      workflows: slice,
      total,
      page,
      per_page: perPage,
      pages: Math.ceil(total / perPage),
    });
  } catch (error) {
    console.error('AI list error:', error);
    res.status(500).json({ error: 'AI list error', details: error.message });
  }
});

app.get('/api/ai/raw/:filename', async (req, res) => {
  try {
    const { filename } = req.params;
    const wf = await db.getWorkflowDetail(filename);
    if (!wf || !wf.raw_workflow) return res.status(404).json({ error: 'Not found' });
    res.setHeader('Content-Type', 'application/json; charset=utf-8');
    res.send(JSON.stringify(wf.raw_workflow));
  } catch (error) {
    console.error('AI raw error:', error);
    res.status(500).json({ error: 'AI raw error', details: error.message });
  }
});

app.get('/api/ai/dataset.ndjson', async (req, res) => {
  try {
    await db.initialize();
    const all = await db.getAllWorkflowsBasic();
    res.setHeader('Content-Type', 'application/x-ndjson; charset=utf-8');
    for (const w of all) {
      const wf = await db.getWorkflowDetail(w.filename);
      const record = {
        filename: w.filename,
        name: w.name,
        category: w.folder || 'Uncategorized',
        node_count: w.node_count,
        trigger_type: w.trigger_type,
        complexity: w.complexity,
        integrations: w.integrations,
        tags: w.tags,
        active: !!w.active,
        raw_json: wf?.raw_workflow || null,
      };
      res.write(JSON.stringify(record) + '\n');
    }
    res.end();
  } catch (error) {
    console.error('AI dataset error:', error);
    res.status(500).json({ error: 'AI dataset error', details: error.message });
  }
});

// Get integrations
app.get('/api/integrations', async (req, res) => {
  try {
    const { workflows } = await db.searchWorkflows('', 'all', 'all', false, 1000, 0);
    
    const integrations = new Set();
    workflows.forEach(workflow => {
      workflow.integrations.forEach(integration => integrations.add(integration));
    });
    
    res.json(Array.from(integrations).sort());
  } catch (error) {
    console.error('Error fetching integrations:', error);
    res.status(500).json({ error: 'Error fetching integrations', details: error.message });
  }
});

// Note: legacy category endpoint above replaced by UI-compatible endpoints

// Error handler
app.use((error, req, res, next) => {
  console.error('Unhandled error:', error);
  res.status(500).json({ 
    error: 'Internal server error', 
    details: process.env.NODE_ENV === 'development' ? error.message : undefined 
  });
});

// 404 handler
app.use((req, res) => {
  res.status(404).json({ error: 'Not found' });
});

// Start server
function startServer(port = 8000, host = '127.0.0.1') {
  const server = app.listen(port, host, () => {
    console.log('🚀 N8N Workflow Documentation Server');
    console.log('=' .repeat(50));
    console.log(`🌐 Server running at http://${host}:${port}`);
    console.log(`📊 API Documentation: http://${host}:${port}/api/stats`);
    console.log(`🔍 Workflow Search: http://${host}:${port}/api/workflows`);
    console.log();
    console.log('Press Ctrl+C to stop the server');
    console.log('-'.repeat(50));
  });
  
  // Graceful shutdown
  process.on('SIGINT', () => {
    console.log('\n👋 Shutting down server...');
    server.close(() => {
      db.close();
      console.log('✅ Server stopped');
      process.exit(0);
    });
  });
}

// CLI interface
if (require.main === module) {
  program
    .option('-p, --port <port>', 'Port to run server on', '8000')
    .option('-h, --host <host>', 'Host to bind to', '127.0.0.1')
    .option('--dev', 'Enable development mode')
    .parse();
  
  const options = program.opts();
  const port = parseInt(options.port);
  const host = options.host;
  
  // Check if database needs initialization
  db.initialize().then(() => db.getStats()).then(async (stats) => {
    if (stats.total === 0) {
      console.log('⚠️  No workflows indexed. Indexing now...');
      try {
        const result = await db.indexWorkflows(true);
        console.log(`✅ Indexed ${result.processed} workflows (skipped: ${result.skipped}, errors: ${result.errors})`);
      } catch (e) {
        console.error('❌ Indexing failed:', e.message);
      }
    } else {
      console.log(`✅ Database ready: ${stats.total} workflows indexed`);
    }
    startServer(port, host);
  }).catch(error => {
    console.error('❌ Database connection failed:', error.message);
    process.exit(1);
  });
}

module.exports = app; 
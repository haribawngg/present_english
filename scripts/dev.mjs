import { spawn } from 'node:child_process';
import { existsSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import path from 'node:path';

const root = fileURLToPath(new URL('../', import.meta.url));
const python = process.env.PYTHON_EXECUTABLE || path.join(
  root, '.venv', process.platform === 'win32' ? 'Scripts/python.exe' : 'bin/python',
);
const viteModule = new URL('../frontend/node_modules/vite/dist/node/index.js', import.meta.url);
let backend;
let frontend;
let stopping = false;

async function stop(code = 0) {
  if (stopping) return;
  stopping = true;
  // Python is launched directly, without a shell or reloader subprocess.
  if (backend && backend.exitCode === null) backend.kill();
  if (frontend) await frontend.close();
  process.exitCode = code;
}

process.on('SIGINT', () => void stop());
process.on('SIGTERM', () => void stop());

function startBackend() {
  return new Promise((resolve, reject) => {
    backend = spawn(python, ['-u', '-m', 'backend.devserver'], {
      cwd: root,
      windowsHide: true,
      stdio: ['ignore', 'pipe', 'inherit'],
      env: { ...process.env, PYTHONUNBUFFERED: '1', TF_CPP_MIN_LOG_LEVEL: '2' },
    });
    const timeout = setTimeout(() => reject(new Error('Backend did not become ready within 120 seconds.')), 120_000);
    let buffer = '';
    backend.stdout.setEncoding('utf8');
    backend.stdout.on('data', chunk => {
      buffer += chunk;
      let newline;
      while ((newline = buffer.indexOf('\n')) >= 0) {
        const line = buffer.slice(0, newline).trim();
        buffer = buffer.slice(newline + 1);
        if (line.startsWith('SMS_LAB_READY=')) {
          clearTimeout(timeout);
          resolve(line.slice('SMS_LAB_READY='.length));
        } else if (line) console.log(`[Flask] ${line}`);
      }
    });
    backend.once('error', error => {
      clearTimeout(timeout);
      reject(error);
    });
    backend.once('exit', code => {
      clearTimeout(timeout);
      reject(new Error(`Backend exited before startup (code ${code}).`));
      if (!stopping) {
        console.error(`Flask stopped (code ${code}).`);
        void stop(code || 1);
      }
    });
  });
}

try {
  if (!existsSync(python)) throw new Error('Python environment missing. Follow the first-time setup in DEMO.md.');
  if (!existsSync(viteModule)) throw new Error('Frontend dependencies missing. Run npm install in the project root.');
  console.log('\nStarting SMS Lab: loading Flask models…');
  const backendUrl = await startBackend();
  if (!stopping) {
    const { createServer } = await import(viteModule.href);
    frontend = await createServer({
      root: path.join(root, 'frontend'),
      configFile: path.join(root, 'frontend/vite.config.ts'),
      server: {
        host: '127.0.0.1',
        port: 5173,
        // Let Vite try 5174, 5175, ... if another application owns 5173.
        strictPort: false,
        open: !process.argv.includes('--no-open'),
        proxy: { '/api': backendUrl },
      },
    });
    if (stopping) await frontend.close();
    else {
      await frontend.listen();
      console.log(`\nFlask API ready: ${backendUrl}`);
      console.log('SMS Lab demo is ready. Press Ctrl+C to stop both servers.\n');
      frontend.printUrls();
    }
  }
} catch (error) {
  console.error(`\nCannot start demo: ${error.message}`);
  await stop(1);
}

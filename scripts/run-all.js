const { spawn } = require('child_process');
const path = require('path');

const commands = [
  {
    name: 'backend',
    command: 'python',
    args: ['backend/run.py'],
  },
  {
    name: 'frontend',
    command: 'npm',
    args: ['--prefix', 'frontend', 'run', 'dev'],
  },
];

function startCommand({ name, command, args }) {
  const proc = spawn(command, args, {
    cwd: path.resolve(__dirname, '..'),
    shell: false,
    stdio: ['ignore', 'pipe', 'pipe'],
  });

  proc.stdout.on('data', (chunk) => {
    process.stdout.write(`[${name}] ${chunk}`);
  });

  proc.stderr.on('data', (chunk) => {
    process.stderr.write(`[${name}] ${chunk}`);
  });

  proc.on('exit', (code, signal) => {
    if (signal) {
      console.log(`[${name}] exited due to signal ${signal}`);
    } else {
      console.log(`[${name}] exited with code ${code}`);
    }
  });

  proc.on('error', (error) => {
    console.error(`[${name}] failed to start: ${error.message}`);
  });

  return proc;
}

commands.forEach(startCommand);

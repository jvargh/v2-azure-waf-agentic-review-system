#!/usr/bin/env node
/**
 * Sequential dev startup:
 * 1. Start backend
 * 2. Poll /api/health until mongo_connected === true or timeout
 * 3. Start frontend
 * Provides diagnostics if falling back to in-memory persistence.
 */

import { spawn, exec } from 'node:child_process';
import { setTimeout as delay } from 'node:timers/promises';

const NPM_CMD = process.platform === 'win32' ? 'npm.cmd' : 'npm';
const BACKEND_CMD = NPM_CMD;
const BACKEND_ARGS = ['run', 'backend'];
const FRONTEND_CMD = NPM_CMD;
const FRONTEND_ARGS = ['run', 'frontend'];
const HEALTH_URL = process.env.API_HEALTH_URL || 'http://localhost:8000/api/health';
const STARTUP_TIMEOUT_MS = parseInt(process.env.STARTUP_TIMEOUT_MS || '45000', 10);
const POLL_INTERVAL_MS = parseInt(process.env.POLL_INTERVAL_MS || '1500', 10);

let backendProc;

function log(msg) {
  console.log(`[dev-seq] ${msg}`);
}

function spawnBackend() {
  const fullCmd = `${BACKEND_CMD} ${BACKEND_ARGS.join(' ')}`;
  log(`Starting backend (exec): ${fullCmd}`);
  backendProc = exec(fullCmd, { shell: true });
  backendProc.stdout.on('data', d => process.stdout.write(`BACKEND: ${d}`));
  backendProc.stderr.on('data', d => process.stderr.write(`BACKEND_ERR: ${d}`));
  backendProc.on('exit', code => {
    log(`Backend process exited with code ${code}`);
    if (!frontendStarted) {
      log('Exiting dev-seq because backend terminated before frontend launch.');
      process.exit(code || 1);
    }
  });
}

async function fetchHealth() {
  try {
    const res = await fetch(HEALTH_URL, { method: 'GET' });
    if (!res.ok) {
      return { ok: false, status: res.status, statusText: res.statusText };
    }
    const data = await res.json();
    return { ok: true, data };
  } catch (err) {
    return { ok: false, error: err.message };
  }
}

async function waitForMongo() {
  log(`Polling health endpoint: ${HEALTH_URL}`);
  const start = Date.now();
  let lastResult = null;
  while (Date.now() - start < STARTUP_TIMEOUT_MS) {
    const result = await fetchHealth();
    lastResult = result;
    if (result.ok && result.data && result.data.mongo_connected) {
      log('Mongo connected. Proceeding to start frontend.');
      return { success: true, result: result.data };
    }
    if (result.ok && result.data) {
      log(`Backend up; mongo_connected=${result.data.mongo_connected}. Waiting...`);
    } else {
      log(`Health check not ready yet (${result.status || result.error || 'unknown'}).`);
    }
    await delay(POLL_INTERVAL_MS);
  }
  log('Timeout waiting for Mongo connectivity. Proceeding anyway.');
  return { success: false, result: (lastResult && lastResult.data) || null };
}

let frontendStarted = false;
function startFrontend(context) {
  frontendStarted = true;
  log('Starting frontend...');
  if (context) {
    log(`Final health snapshot: mongo_connected=${context.mongo_connected} using_in_memory=${context.using_in_memory}`);
    if (context.error) {
      log(`Mongo error detail: ${context.error}`);
    }
  } else {
    log('No health data available at launch.');
  }
  const feCmd = `${FRONTEND_CMD} ${FRONTEND_ARGS.join(' ')}`;
  const fe = exec(feCmd, { shell: true });
  fe.stdout.on('data', d => process.stdout.write(`FRONTEND: ${d}`));
  fe.stderr.on('data', d => process.stderr.write(`FRONTEND_ERR: ${d}`));
  fe.on('exit', code => {
    log(`Frontend process exited with code ${code}`);
  });
}

async function main() {
  spawnBackend();
  const { success, result } = await waitForMongo();
  if (!success && result && result.using_in_memory) {
    log('Proceeding with in-memory persistence (Mongo unavailable).');
  } else if (!success) {
    log('Proceeding without confirmed Mongo state.');
  }
  startFrontend(result);
}

main().catch(err => {
  log(`Fatal error: ${err.stack || err.message}`);
  process.exit(1);
});

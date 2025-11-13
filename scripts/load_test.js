/**
 * ADA.SEA Load Testing Script
 * Uses k6 for performance testing
 *
 * Install: https://k6.io/docs/getting-started/installation/
 * Run: k6 run scripts/load_test.js
 */

import http from 'k6/http';
import { check, sleep } from 'k6';
import { Rate } from 'k6/metrics';

// Custom metrics
const errorRate = new Rate('errors');

// Load test configuration
export const options = {
  stages: [
    { duration: '30s', target: 10 },   // Ramp up to 10 users
    { duration: '1m', target: 50 },    // Ramp up to 50 users
    { duration: '2m', target: 100 },   // Ramp up to 100 users
    { duration: '1m', target: 50 },    // Ramp down to 50 users
    { duration: '30s', target: 0 },    // Ramp down to 0 users
  ],
  thresholds: {
    'http_req_duration': ['p(95)<500'], // 95% of requests must complete below 500ms
    'http_req_failed': ['rate<0.01'],   // Error rate must be below 1%
    'errors': ['rate<0.1'],             // Custom error rate below 10%
  },
};

const BASE_URL = __ENV.BASE_URL || 'http://localhost:8000';

// Test scenarios
export default function () {
  // Scenario 1: Health check
  const healthCheck = http.get(`${BASE_URL}/health`);
  check(healthCheck, {
    'health check is 200': (r) => r.status === 200,
    'health check has status': (r) => r.json('status') === 'healthy',
  }) || errorRate.add(1);

  sleep(1);

  // Scenario 2: Privacy status check
  const privacyStatus = http.get(`${BASE_URL}/api/v1/privacy/status`);
  check(privacyStatus, {
    'privacy status is 200': (r) => r.status === 200,
    'privacy edge_only is true': (r) => r.json('edge_only_mode') === true,
    'privacy cloud_sync is false': (r) => r.json('cloud_sync_enabled') === false,
  }) || errorRate.add(1);

  sleep(1);

  // Scenario 3: Voice command (simulated)
  const voiceCommand = http.post(
    `${BASE_URL}/api/v1/privacy/voice-command`,
    JSON.stringify({
      command: "Ada, gizlilik durumunu göster",
      captain_id: `test_captain_${__VU}`,
      language: "tr"
    }),
    {
      headers: { 'Content-Type': 'application/json' },
    }
  );
  check(voiceCommand, {
    'voice command is 200': (r) => r.status === 200,
  }) || errorRate.add(1);

  sleep(2);

  // Scenario 4: Captain privacy status
  const captainId = `test_captain_${__VU}`;
  const captainStatus = http.get(
    `${BASE_URL}/api/v1/privacy/captain/${captainId}/status?language=tr`
  );
  check(captainStatus, {
    'captain status is 200': (r) => r.status === 200,
    'captain status has success': (r) => r.json('success') === true,
  }) || errorRate.add(1);

  sleep(1);

  // Scenario 5: Sharing history
  const history = http.get(
    `${BASE_URL}/api/v1/privacy/captain/${captainId}/history?days=7&language=tr`
  );
  check(history, {
    'history is 200': (r) => r.status === 200,
  }) || errorRate.add(1);

  sleep(1);

  // Scenario 6: API documentation
  const docs = http.get(`${BASE_URL}/docs`);
  check(docs, {
    'docs is 200': (r) => r.status === 200,
  }) || errorRate.add(1);

  sleep(1);
}

// Setup function (runs once at start)
export function setup() {
  console.log('Starting ADA.SEA load test...');
  console.log(`Base URL: ${BASE_URL}`);
}

// Teardown function (runs once at end)
export function teardown() {
  console.log('Load test complete!');
}

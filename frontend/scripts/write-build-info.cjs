/**
 * Writes public/build-info.json before production build so deployed UIs can show the git commit.
 * CI can set REACT_APP_GIT_SHA / VERCEL_GIT_COMMIT_SHA / GITHUB_SHA / CF_PAGES_COMMIT_SHA instead.
 */
const fs = require('fs');
const path = require('path');
const { execSync } = require('child_process');

const frontendRoot = path.join(__dirname, '..');
const repoRoot = path.join(frontendRoot, '..');
const outPath = path.join(frontendRoot, 'public', 'build-info.json');

let commit =
  process.env.REACT_APP_GIT_SHA ||
  process.env.VERCEL_GIT_COMMIT_SHA ||
  process.env.GITHUB_SHA ||
  process.env.CF_PAGES_COMMIT_SHA;

if (!commit) {
  try {
    commit = execSync('git rev-parse HEAD', { encoding: 'utf8', cwd: repoRoot }).trim();
  } catch {
    commit = 'unknown';
  }
}

const payload = {
  commit,
  builtAt: new Date().toISOString(),
};

fs.mkdirSync(path.dirname(outPath), { recursive: true });
fs.writeFileSync(outPath, `${JSON.stringify(payload, null, 2)}\n`, 'utf8');
console.log('[write-build-info]', outPath, commit);

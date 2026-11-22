#!/usr/bin/env node
// news-image-20261123 — entrypoint.
// Renders entry.png with draw_image.py, checks the PNG (magic bytes,
// at most 1 MiB, exactly 1024x1024, 8-bit RGB/RGBA), renders a second
// time and demands byte-identical output, then copies the result to
// $MAKEFUN_OUTPUT_DIR (default /output). When drawing fails, the
// committed entry.png is used as a fallback so the entry still ships;
// the fallback is validated the same way before it is copied.
import { spawnSync } from "node:child_process";
import { createHash } from "node:crypto";
import { copyFileSync, existsSync, mkdirSync, readFileSync, statSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const HERE = dirname(fileURLToPath(import.meta.url));
const ENTRY = join(HERE, "entry.png");
const DRAW = join(HERE, "draw_image.py");
const MAX_BYTES = 1024 * 1024;
const MAGIC = Buffer.from([0x89, 0x50, 0x4e, 0x47, 0x0d, 0x0a, 0x1a, 0x0a]);
const TAG = "[news-image-20261123]";

function die(msg) {
  console.error(`${TAG} ERROR: ${msg}`);
  process.exit(1);
}

function hashOf(path) {
  return createHash("sha256").update(readFileSync(path)).digest("hex");
}

function checkPng(path) {
  if (!existsSync(path)) die(`missing file: ${path}`);
  const bytes = statSync(path).size;
  if (bytes > MAX_BYTES) die(`${path} is ${bytes} bytes, over the 1 MiB limit`);
  const buf = readFileSync(path);
  if (!buf.subarray(0, 8).equals(MAGIC)) die(`${path} lacks the PNG magic bytes`);
  const w = buf.readUInt32BE(16);
  const h = buf.readUInt32BE(20);
  if (w !== 1024 || h !== 1024) die(`${path} is ${w}x${h}, expected 1024x1024`);
  if (buf[24] !== 8) die(`${path} has bit depth ${buf[24]}, expected 8`);
  if (buf[25] !== 2 && buf[25] !== 6) {
    die(`${path} has colour type ${buf[25]}, expected RGB (2) or RGBA (6)`);
  }
}

function draw() {
  if (!existsSync(DRAW)) {
    console.warn(`${TAG} draw script missing: ${DRAW}`);
    return false;
  }
  const res = spawnSync("python3", [DRAW], {
    cwd: HERE,
    stdio: "inherit",
    env: { ...process.env, TMPDIR: process.env.TMPDIR ?? join(HERE, "..", "tmpgrade") },
  });
  return res.status === 0;
}

const outDir = process.env.MAKEFUN_OUTPUT_DIR ?? "/output";
mkdirSync(outDir, { recursive: true });
const target = join(outDir, "entry.png");

if (draw()) {
  const first = hashOf(ENTRY);
  if (!draw()) die("second render failed during the determinism check");
  const second = hashOf(ENTRY);
  if (first !== second) die(`renders differ: ${first} vs ${second}`);
  console.log(`${TAG} determinism OK: two renders identical (${first})`);
  console.log(`${TAG} entry.png freshly rendered by draw_image.py`);
} else {
  console.warn(`${TAG} draw failed, falling back to committed entry.png`);
}

if (!existsSync(ENTRY)) die("entry.png is missing and no committed fallback exists");
checkPng(ENTRY);
copyFileSync(ENTRY, target);
checkPng(target);
console.log(
  `${TAG} OK: ${target} (${statSync(target).size} bytes, 1024x1024, sha256 ${hashOf(target)})`,
);

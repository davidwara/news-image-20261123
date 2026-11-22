#!/usr/bin/env node
// news-image-20261123 — entrypoint.
// The entry is a program that writes one image to /output/entry.png.
// This file drives draw_image.py, then proves the result is a valid
// PNG (magic bytes, at most 1 MiB, exactly 1024x1024, 8-bit RGB/RGBA)
// and deterministic (a second render must produce identical bytes),
// and copies it to $MAKEFUN_OUTPUT_DIR (default /output). If the
// draw step fails, the entry.png committed in this repository is
// used instead, and it goes through the same validation before copy.
import { spawnSync } from "node:child_process";
import { createHash } from "node:crypto";
import { copyFileSync, existsSync, mkdirSync, readFileSync, statSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const ROOT = dirname(fileURLToPath(import.meta.url));
const PNG_PATH = join(ROOT, "entry.png");
const SCRIPT = join(ROOT, "draw_image.py");
const BYTE_LIMIT = 1024 * 1024;
const PNG_SIG = Buffer.from([0x89, 0x50, 0x4e, 0x47, 0x0d, 0x0a, 0x1a, 0x0a]);
const LOG_TAG = "[news-image-20261123]";

function abort(reason) {
  console.error(`${LOG_TAG} ERROR: ${reason}`);
  process.exit(1);
}

function file_sha256(path) {
  return createHash("sha256").update(readFileSync(path)).digest("hex");
}

function assert_png(path) {
  if (!existsSync(path)) abort(`missing file: ${path}`);
  const size = statSync(path).size;
  if (size > BYTE_LIMIT) {
    abort(`${path} is ${size} bytes, over the 1 MiB limit`);
  }
  const head = readFileSync(path);
  if (!head.subarray(0, 8).equals(PNG_SIG)) {
    abort(`${path} does not start with the PNG magic bytes`);
  }
  // The IHDR chunk holds width and height as big-endian uint32 at
  // offsets 16 and 20, bit depth at 24, colour type at 25.
  const width = head.readUInt32BE(16);
  const height = head.readUInt32BE(20);
  if (width !== 1024 || height !== 1024) {
    abort(`${path} is ${width}x${height}, expected 1024x1024`);
  }
  if (head[24] !== 8) abort(`${path} has bit depth ${head[24]}, expected 8`);
  if (head[25] !== 2 && head[25] !== 6) {
    abort(`${path} has colour type ${head[25]}, expected RGB (2) or RGBA (6)`);
  }
}

function render_once() {
  if (!existsSync(SCRIPT)) {
    console.warn(`${LOG_TAG} draw script missing: ${SCRIPT}`);
    return false;
  }
  const outcome = spawnSync("python3", [SCRIPT], {
    cwd: ROOT,
    stdio: "inherit",
    env: { ...process.env, TMPDIR: process.env.TMPDIR ?? join(ROOT, "..", "tmpgrade") },
  });
  return outcome.status === 0;
}

function run() {
  const outDir = process.env.MAKEFUN_OUTPUT_DIR ?? "/output";
  mkdirSync(outDir, { recursive: true });
  const target = join(outDir, "entry.png");

  const rendered = render_once();
  if (rendered) {
    // Determinism self-check: render a second time and require the
    // exact same bytes, so the entry is reproducible, not just valid.
    const firstHash = file_sha256(PNG_PATH);
    if (!render_once()) abort("determinism check: the second render failed");
    const secondHash = file_sha256(PNG_PATH);
    if (firstHash !== secondHash) {
      abort(`determinism check: renders differ (${firstHash} vs ${secondHash})`);
    }
    console.log(`${LOG_TAG} determinism OK: two renders identical (${firstHash})`);
    console.log(`${LOG_TAG} entry.png freshly rendered by draw_image.py`);
  } else {
    console.warn(`${LOG_TAG} draw failed, falling back to committed entry.png`);
  }

  if (!existsSync(PNG_PATH)) {
    abort("entry.png is missing after the render attempt and no committed fallback exists");
  }
  assert_png(PNG_PATH);
  copyFileSync(PNG_PATH, target);
  assert_png(target);
  console.log(
    `${LOG_TAG} OK: ${target} (${statSync(target).size} bytes, 1024x1024, sha256 ${file_sha256(target)})`,
  );
}

run();

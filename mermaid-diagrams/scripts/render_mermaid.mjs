#!/usr/bin/env node
import { spawnSync } from "node:child_process";
import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import { fileURLToPath } from "node:url";

const FENCE_RE = /```(?:mermaid|mmd)\s*\n(?<body>[\s\S]*?)\n```/gi;
const SCRIPT_DIR = path.dirname(fileURLToPath(import.meta.url));
const SKILL_DIR = path.resolve(SCRIPT_DIR, "..");
const PACKAGE_JSON = path.join(SKILL_DIR, "package.json");
const REQUIRED_PACKAGES = [
  "mermaid",
  "jsdom",
  "@resvg/resvg-js",
  "@fontsource/noto-sans",
  "image-size",
  "pngjs",
  "zod",
];
const NOTO_SANS_DIR = path.join(SKILL_DIR, "node_modules", "@fontsource", "noto-sans", "files");
const NOTO_SANS_FONTS = [
  {
    weight: 400,
    style: "normal",
    files: ["noto-sans-latin-400-normal.woff2", "noto-sans-cyrillic-400-normal.woff2"],
  },
  {
    weight: 700,
    style: "normal",
    files: ["noto-sans-latin-700-normal.woff2", "noto-sans-cyrillic-700-normal.woff2"],
  },
  {
    weight: 400,
    style: "italic",
    files: ["noto-sans-latin-400-italic.woff2", "noto-sans-cyrillic-400-italic.woff2"],
  },
];
const RENDERER_LABEL = "mermaid + jsdom + @resvg/resvg-js + Noto Sans + PNG gates";
const OUTPUT_VIEWBOX_PADDING = 32;

function usage() {
  return `Render Mermaid .mmd or a single Markdown Mermaid fence to PNG without Chromium.

Usage:
  node scripts/render_mermaid.mjs --input diagram.mmd --output diagram.png --json
  node scripts/render_mermaid.mjs --input README.md --output diagram.png --install

Options:
  -i, --input <path>       Input .mmd file or Markdown file with one Mermaid fence.
  -o, --output <path>      Output PNG path. Must end with .png.
  --svg-output <path>      Optional debug SVG output path.
  --theme <name>           Mermaid theme. Default: default.
  --background <value>     PNG background. Use transparent for alpha. Default: white.
  --width <number>         Output PNG width. Defaults to rendered SVG viewBox width.
  --height <number>        Output PNG height. Defaults to rendered SVG viewBox height.
  --scale <number>         Scale factor when width/height are omitted. Default: 2.
  --install                Run npm install in the skill directory if local Node deps are missing.
  --check-tools            Only report local renderer availability. Does not require input or output.
  --json                   Print structured JSON.
  -h, --help               Show this help.

Exit codes:
  0  success, or --check-tools completed
  1  render command failed
  2  invalid input or arguments
  3  local Node renderer dependencies unavailable
  4  rendered PNG failed metadata or pixel sanity gates`;
}

function parseArgs(argv) {
  const args = {
    theme: "default",
    background: "white",
    scale: 2,
    install: false,
    checkTools: false,
    json: false,
    help: false,
  };

  for (let index = 0; index < argv.length; index += 1) {
    const token = argv[index];
    const value = () => {
      if (index + 1 >= argv.length) throw new Error(`Missing value for ${token}`);
      index += 1;
      return argv[index];
    };

    switch (token) {
      case "-i":
      case "--input":
        args.input = value();
        break;
      case "-o":
      case "--output":
        args.output = value();
        break;
      case "--svg-output":
        args.svgOutput = value();
        break;
      case "--theme":
        args.theme = value();
        break;
      case "--background":
        args.background = value();
        break;
      case "--width":
        args.width = Number(value());
        break;
      case "--height":
        args.height = Number(value());
        break;
      case "--scale":
        args.scale = Number(value());
        break;
      case "--install":
        args.install = true;
        break;
      case "--check-tools":
        args.checkTools = true;
        break;
      case "--json":
        args.json = true;
        break;
      case "-h":
      case "--help":
        args.help = true;
        break;
      default:
        throw new Error(`Unknown argument: ${token}`);
    }
  }

  if (!Number.isFinite(args.scale) || args.scale <= 0) {
    throw new Error("--scale must be a positive number.");
  }
  for (const key of ["width", "height"]) {
    if (args[key] !== undefined && (!Number.isFinite(args[key]) || args[key] <= 0)) {
      throw new Error(`--${key} must be a positive number.`);
    }
  }
  return args;
}

function emit(payload, asJson) {
  if (asJson) {
    process.stdout.write(`${JSON.stringify(payload, null, 2)}\n`);
    return;
  }

  const status = payload.ok ? "OK" : "FAIL";
  process.stdout.write(`${status}: ${payload.message ?? ""}\n`);
  if (payload.renderer) process.stdout.write(`renderer: ${payload.renderer}\n`);
  if (payload.output) process.stdout.write(`output: ${payload.output}\n`);
  if (payload.svg_output) process.stdout.write(`svg: ${payload.svg_output}\n`);
  if (payload.stderr) process.stderr.write(`${payload.stderr}\n`);
}

async function getProtocolSchema() {
  const { z } = await import("zod");
  const gateSchema = z.object({
    status: z.enum(["PASS", "FAIL", "REQUIRED", "SKIPPED"]),
    message: z.string().optional(),
  });

  return z
    .object({
      ok: z.boolean(),
      message: z.string(),
      renderer: z.string().nullable().optional(),
      input: z.string().optional(),
      output: z.string().optional(),
      svg_output: z.string().nullable().optional(),
      bytes: z.number().int().nonnegative().optional(),
      width: z.number().positive().optional(),
      height: z.number().positive().optional(),
      metadata: z
        .object({
          type: z.string(),
          width: z.number().positive(),
          height: z.number().positive(),
          bytes: z.number().int().nonnegative(),
        })
        .optional(),
      pixel_sanity: z
        .object({
          total_pixels: z.number().int().positive(),
          sampled_pixels: z.number().int().positive(),
          unique_colors: z.number().int().nonnegative(),
          non_transparent_pixels: z.number().int().nonnegative(),
          different_from_corner_pixels: z.number().int().nonnegative(),
          non_transparent_ratio: z.number().min(0).max(1),
          different_from_corner_ratio: z.number().min(0).max(1),
          dominant_color_ratio: z.number().min(0).max(1),
        })
        .optional(),
      gates: z
        .object({
          source: gateSchema,
          render: gateSchema,
          png_metadata: gateSchema.optional(),
          png_pixel: gateSchema.optional(),
          visual: gateSchema.optional(),
        })
        .optional(),
      required_next_action: z.string().optional(),
      required_packages: z.array(z.string()).optional(),
      missing_packages: z.array(z.string()).optional(),
      package_json: z.string().optional(),
      install_attempted: z.boolean().optional(),
      install_result: z.unknown().optional(),
      install_command: z.string().optional(),
      stack: z.string().optional(),
      stderr: z.string().optional(),
    })
    .passthrough();
}

function emitProtocol(payload, asJson, schema) {
  const result = schema.safeParse(payload);
  if (!result.success) {
    emit(
      {
        ok: false,
        message: "Internal JSON protocol validation failed",
        renderer: payload.renderer ?? null,
        zod_issues: result.error.issues,
        original_payload: payload,
      },
      asJson,
    );
    return false;
  }

  emit(result.data, asJson);
  return true;
}

function findExecutable(name) {
  const pathValue = process.env.PATH ?? "";
  const extensions = process.platform === "win32" ? [".cmd", ".exe", ".bat", ""] : [""];
  for (const dir of pathValue.split(path.delimiter)) {
    if (!dir) continue;
    for (const ext of extensions) {
      const candidate = path.join(dir, `${name}${ext}`);
      try {
        fs.accessSync(candidate, fs.constants.X_OK);
        return candidate;
      } catch {
        // Keep looking.
      }
    }
  }
  return null;
}

async function checkDependencies() {
  const missing = [];
  for (const packageName of REQUIRED_PACKAGES) {
    try {
      import.meta.resolve(packageName);
    } catch {
      missing.push(packageName);
    }
  }
  for (const font of NOTO_SANS_FONTS.flatMap((entry) => entry.files)) {
    if (!fs.existsSync(path.join(NOTO_SANS_DIR, font))) {
      missing.push(`@fontsource/noto-sans/files/${font}`);
    }
  }
  return { ok: missing.length === 0, missing };
}

function installLocalRenderer() {
  const npm = findExecutable("npm");
  if (!npm) {
    return {
      ok: false,
      message: "npm executable not found; cannot install local Node renderer.",
      command: null,
      stdout: "",
      stderr: "",
    };
  }
  if (!fs.existsSync(PACKAGE_JSON)) {
    return {
      ok: false,
      message: `package.json not found: ${PACKAGE_JSON}`,
      command: null,
      stdout: "",
      stderr: "",
    };
  }

  const command = [npm, "install", "--omit=dev", "--no-audit", "--fund=false"];
  const result = spawnSync(command[0], command.slice(1), {
    cwd: SKILL_DIR,
    encoding: "utf8",
    windowsHide: true,
  });

  return {
    ok: !result.error && result.status === 0,
    message: !result.error && result.status === 0 ? "Local Node renderer installed" : "npm install failed",
    command: ["npm", "install", "--omit=dev", "--no-audit", "--fund=false"],
    stdout: result.stdout?.trim() ?? "",
    stderr: result.error ? `${result.error.message}\n${result.stderr ?? ""}`.trim() : (result.stderr?.trim() ?? ""),
  };
}

function shellQuote(value) {
  return `'${String(value).replace(/'/g, "'\\''")}'`;
}

function prepareInput(inputPath, tempDir) {
  if (!fs.existsSync(inputPath)) {
    throw new Error(`Input file not found: ${inputPath}`);
  }
  if (![".md", ".markdown"].includes(path.extname(inputPath).toLowerCase())) {
    return fs.readFileSync(inputPath, "utf8").trim() + "\n";
  }

  const text = fs.readFileSync(inputPath, "utf8");
  const matches = [...text.matchAll(FENCE_RE)];
  if (matches.length !== 1) {
    throw new Error(`Expected exactly one Mermaid fence in Markdown, found ${matches.length}: ${inputPath}`);
  }

  const extracted = path.join(tempDir, "extracted.mmd");
  const source = `${matches[0].groups.body.trim()}\n`;
  fs.writeFileSync(extracted, source, "utf8");
  return source;
}

function fontBuffers() {
  return NOTO_SANS_FONTS.flatMap((entry) => entry.files.map((file) => path.join(NOTO_SANS_DIR, file)))
    .filter((file) => fs.existsSync(file))
    .map((file) => fs.readFileSync(file));
}

function fontFaceCss() {
  return NOTO_SANS_FONTS.flatMap((entry) =>
    entry.files
      .map((file) => path.join(NOTO_SANS_DIR, file))
      .filter((file) => fs.existsSync(file))
      .map((file) => {
        const data = fs.readFileSync(file).toString("base64");
        return `@font-face{font-family:"Noto Sans";font-style:${entry.style};font-weight:${entry.weight};font-display:block;src:url(data:font/woff2;base64,${data}) format("woff2");}`;
      }),
  ).join("\n");
}

function injectFontCss(svg) {
  const css = `${fontFaceCss()}\nsvg, text, tspan { font-family: "Noto Sans", sans-serif !important; }`;
  if (/<style\b[^>]*>/i.test(svg)) {
    return svg.replace(/<style\b([^>]*)>/i, `<style$1>${css}\n`);
  }
  return svg.replace(/<svg\b[^>]*>/i, (tag) => `${tag}<style>${css}</style>`);
}

function escapeAttr(value) {
  return String(value)
    .replace(/&/g, "&amp;")
    .replace(/"/g, "&quot;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;");
}

function injectBackgroundRect(svg, background, viewBox, width, height) {
  if (background === "transparent") return svg;
  const x = viewBox?.x ?? 0;
  const y = viewBox?.y ?? 0;
  const rectWidth = viewBox?.width ?? width;
  const rectHeight = viewBox?.height ?? height;
  const rect = `<rect x="${x}" y="${y}" width="${rectWidth}" height="${rectHeight}" fill="${escapeAttr(background)}"/>`;
  return svg.replace(/<svg\b[^>]*>/i, (tag) => `${tag}${rect}`);
}

function setRootSvgAttr(svg, name, value) {
  const attrRe = new RegExp(`\\b${name}=["'][^"']*["']`, "i");
  return svg.replace(/<svg\b[^>]*>/i, (tag) => {
    if (attrRe.test(tag)) {
      return tag.replace(attrRe, `${name}="${value}"`);
    }
    return tag.replace(/<svg\b/i, `<svg ${name}="${value}"`);
  });
}

function rootSvgHasAttr(svg, name, value) {
  const rootMatch = svg.match(/<svg\b[^>]*>/i);
  if (!rootMatch) return false;
  return new RegExp(`\\b${name}=["']${value.replace(/[.*+?^${}()|[\]\\]/g, "\\$&")}["']`, "i").test(rootMatch[0]);
}

function validateRenderArgs(args) {
  if (!args.input || !args.output) {
    throw new Error("--input and --output are required unless --check-tools is used.");
  }

  const inputPath = path.resolve(args.input);
  const outputPath = path.resolve(args.output);
  if (path.extname(outputPath).toLowerCase() !== ".png") {
    throw new Error("Output path must end with .png for the mandatory PNG gate.");
  }

  const svgOutputPath = args.svgOutput ? path.resolve(args.svgOutput) : null;
  if (svgOutputPath && path.extname(svgOutputPath).toLowerCase() !== ".svg") {
    throw new Error("--svg-output must end with .svg.");
  }

  fs.mkdirSync(path.dirname(outputPath), { recursive: true });
  if (svgOutputPath) fs.mkdirSync(path.dirname(svgOutputPath), { recursive: true });
  return { inputPath, outputPath, svgOutputPath };
}

function estimateText(element) {
  const text = (element.textContent ?? "").replace(/\s+/g, " ").trim();
  const fontSize =
    Number.parseFloat(element.getAttribute("font-size") ?? "") ||
    Number.parseFloat(element.style?.fontSize ?? "") ||
    16;
  const lines = Math.max(1, text.split(/\n|<br\s*\/?>/i).length);
  const maxLineLength = Math.max(1, ...text.split(/\n|<br\s*\/?>/i).map((line) => line.length));
  return {
    width: Math.max(8, maxLineLength * fontSize * 0.62),
    height: Math.max(16, lines * fontSize * 1.25),
  };
}

function installSvgMeasurementPolyfills(window) {
  const svgElement = window.SVGElement?.prototype;
  if (!svgElement) return;

  if (!svgElement.getBBox) {
    svgElement.getBBox = function getBBox() {
      const tag = this.tagName?.toLowerCase();
      if (tag === "text" || tag === "tspan") {
        const box = estimateText(this);
        return { x: 0, y: 0, width: box.width, height: box.height };
      }

      const width =
        Number.parseFloat(this.getAttribute?.("width") ?? "") ||
        Number.parseFloat(this.style?.width ?? "") ||
        estimateText(this).width;
      const height =
        Number.parseFloat(this.getAttribute?.("height") ?? "") ||
        Number.parseFloat(this.style?.height ?? "") ||
        estimateText(this).height;
      const x = Number.parseFloat(this.getAttribute?.("x") ?? "") || 0;
      const y = Number.parseFloat(this.getAttribute?.("y") ?? "") || 0;
      return { x, y, width, height };
    };
  }

  if (!svgElement.getComputedTextLength) {
    svgElement.getComputedTextLength = function getComputedTextLength() {
      return estimateText(this).width;
    };
  }

  if (!svgElement.getScreenCTM) {
    svgElement.getScreenCTM = () => ({
      a: 1,
      b: 0,
      c: 0,
      d: 1,
      e: 0,
      f: 0,
      inverse() {
        return this;
      },
      multiply() {
        return this;
      },
    });
  }
}

function installDomGlobals(dom) {
  const window = dom.window;
  installSvgMeasurementPolyfills(window);

  class BasicCSSStyleSheet {
    constructor() {
      this.cssRules = [];
    }

    insertRule(rule, index = this.cssRules.length) {
      this.cssRules.splice(index, 0, { cssText: rule });
      return index;
    }

    replaceSync(text) {
      this.cssRules = String(text)
        .split("}")
        .map((rule) => rule.trim())
        .filter(Boolean)
        .map((rule) => ({ cssText: `${rule}}` }));
    }
  }

  const values = {
    window,
    document: window.document,
    navigator: window.navigator,
    Element: window.Element,
    HTMLElement: window.HTMLElement,
    SVGElement: window.SVGElement,
    SVGGraphicsElement: window.SVGGraphicsElement ?? window.SVGElement,
    Node: window.Node,
    DOMParser: window.DOMParser,
    XMLSerializer: window.XMLSerializer,
    CSSStyleSheet: window.CSSStyleSheet ?? BasicCSSStyleSheet,
    getComputedStyle: window.getComputedStyle.bind(window),
    requestAnimationFrame: window.requestAnimationFrame ?? ((callback) => setTimeout(callback, 0)),
    cancelAnimationFrame: window.cancelAnimationFrame ?? ((handle) => clearTimeout(handle)),
  };

  const previous = new Map();
  for (const [key, value] of Object.entries(values)) {
    previous.set(key, Object.getOwnPropertyDescriptor(globalThis, key));
    Object.defineProperty(globalThis, key, {
      value,
      configurable: true,
      writable: true,
    });
  }

  return () => {
    for (const [key, descriptor] of previous.entries()) {
      if (descriptor) Object.defineProperty(globalThis, key, descriptor);
      else delete globalThis[key];
    }
    window.close();
  };
}

function parseViewBox(svg) {
  const match = svg.match(/\bviewBox=["']([^"']+)["']/i);
  if (!match) return null;
  const parts = match[1].trim().split(/[\s,]+/).map(Number);
  if (parts.length !== 4 || parts.some((part) => !Number.isFinite(part))) return null;
  return { x: parts[0], y: parts[1], width: parts[2], height: parts[3] };
}

function padViewBox(viewBox, padding = OUTPUT_VIEWBOX_PADDING) {
  if (!viewBox) return null;
  return {
    x: viewBox.x - padding,
    y: viewBox.y - padding,
    width: viewBox.width + padding * 2,
    height: viewBox.height + padding * 2,
  };
}

function parseTranslate(value) {
  const match = String(value ?? "").match(/translate\(\s*([-.\d]+)(?:[\s,]+([-.\d]+))?\s*\)/);
  if (!match) return { x: 0, y: 0 };
  return {
    x: Number.parseFloat(match[1]) || 0,
    y: Number.parseFloat(match[2] ?? "0") || 0,
  };
}

function mergeBounds(bounds, box) {
  if (!box || !Number.isFinite(box.x) || !Number.isFinite(box.y) || !Number.isFinite(box.width) || !Number.isFinite(box.height)) {
    return bounds;
  }
  if (box.width <= 0 || box.height <= 0) return bounds;
  const x1 = box.x;
  const y1 = box.y;
  const x2 = box.x + box.width;
  const y2 = box.y + box.height;
  if (!bounds) return { x1, y1, x2, y2 };
  return {
    x1: Math.min(bounds.x1, x1),
    y1: Math.min(bounds.y1, y1),
    x2: Math.max(bounds.x2, x2),
    y2: Math.max(bounds.y2, y2),
  };
}

function extractNumericPairs(value) {
  const numbers = String(value ?? "").match(/-?\d*\.?\d+(?:e[-+]?\d+)?/gi)?.map(Number) ?? [];
  const pairs = [];
  for (let index = 0; index + 1 < numbers.length; index += 2) {
    pairs.push([numbers[index], numbers[index + 1]]);
  }
  return pairs;
}

function computeContentViewBox(svg) {
  const nodeGroupRe = /<g\b(?=[^>]*\bclass=["'][^"']*\bnode\b)(?=[^>]*\btransform=["']([^"']+)["'])[^>]*>[\s\S]*?<rect\b([^>]*)>/gi;
  const nodePathGroupRe = /<g\b(?=[^>]*\bclass=["'][^"']*\bnode\b)(?=[^>]*\btransform=["']([^"']+)["'])[^>]*>[\s\S]*?<path\b[^>]*\bd=["']([^"']+)["'][^>]*>/gi;
  const rectRe = /<rect\b[^>]*>/gi;
  const circleRe = /<circle\b[^>]*>/gi;
  const ellipseRe = /<ellipse\b[^>]*>/gi;
  const pathRe = /<path\b[^>]*\bd=["']([^"']+)["'][^>]*>/gi;
  const polygonRe = /<(?:polygon|polyline)\b[^>]*\bpoints=["']([^"']+)["'][^>]*>/gi;
  const textRe = /<text\b[^>]*>([\s\S]*?)<\/text>/gi;
  let bounds = null;

  const attr = (tag, name) => {
    const match = tag.match(new RegExp(`\\b${name}=["']([^"']+)["']`, "i"));
    return match ? Number.parseFloat(match[1]) : 0;
  };

  const translatedBox = (tag, box) => {
    const translate = parseTranslate(tag.match(/\btransform=["']([^"']+)["']/i)?.[1]);
    return { ...box, x: box.x + translate.x, y: box.y + translate.y };
  };

  for (const match of svg.matchAll(nodeGroupRe)) {
    const translate = parseTranslate(match[1]);
    const rectTag = match[2];
    bounds = mergeBounds(bounds, {
      x: attr(rectTag, "x") + translate.x,
      y: attr(rectTag, "y") + translate.y,
      width: attr(rectTag, "width"),
      height: attr(rectTag, "height"),
    });
  }

  for (const match of svg.matchAll(nodePathGroupRe)) {
    const translate = parseTranslate(match[1]);
    const points = extractNumericPairs(match[2]);
    if (points.length === 0) continue;
    const xs = points.map(([x]) => x);
    const ys = points.map(([, y]) => y);
    bounds = mergeBounds(bounds, {
      x: Math.min(...xs) + translate.x,
      y: Math.min(...ys) + translate.y,
      width: Math.max(...xs) - Math.min(...xs),
      height: Math.max(...ys) - Math.min(...ys),
    });
  }

  for (const match of svg.matchAll(rectRe)) {
    const tag = match[0];
    bounds = mergeBounds(
      bounds,
      translatedBox(tag, {
        x: attr(tag, "x"),
        y: attr(tag, "y"),
        width: attr(tag, "width"),
        height: attr(tag, "height"),
      }),
    );
  }

  for (const match of svg.matchAll(circleRe)) {
    const tag = match[0];
    const r = attr(tag, "r");
    bounds = mergeBounds(bounds, translatedBox(tag, { x: attr(tag, "cx") - r, y: attr(tag, "cy") - r, width: r * 2, height: r * 2 }));
  }

  for (const match of svg.matchAll(ellipseRe)) {
    const tag = match[0];
    const rx = attr(tag, "rx");
    const ry = attr(tag, "ry");
    bounds = mergeBounds(bounds, translatedBox(tag, { x: attr(tag, "cx") - rx, y: attr(tag, "cy") - ry, width: rx * 2, height: ry * 2 }));
  }

  for (const match of svg.matchAll(pathRe)) {
    const points = extractNumericPairs(match[1]);
    if (points.length === 0) continue;
    const xs = points.map(([x]) => x);
    const ys = points.map(([, y]) => y);
    const translate = parseTranslate(match[0].match(/\btransform=["']([^"']+)["']/i)?.[1]);
    bounds = mergeBounds(bounds, {
      x: Math.min(...xs) + translate.x,
      y: Math.min(...ys) + translate.y,
      width: Math.max(...xs) - Math.min(...xs),
      height: Math.max(...ys) - Math.min(...ys),
    });
  }

  for (const match of svg.matchAll(polygonRe)) {
    const points = extractNumericPairs(match[1]);
    if (points.length === 0) continue;
    const xs = points.map(([x]) => x);
    const ys = points.map(([, y]) => y);
    const translate = parseTranslate(match[0].match(/\btransform=["']([^"']+)["']/i)?.[1]);
    bounds = mergeBounds(bounds, {
      x: Math.min(...xs) + translate.x,
      y: Math.min(...ys) + translate.y,
      width: Math.max(...xs) - Math.min(...xs),
      height: Math.max(...ys) - Math.min(...ys),
    });
  }

  for (const match of svg.matchAll(textRe)) {
    const tag = match[0];
    const text = match[1].replace(/<[^>]+>/g, " ").replace(/\s+/g, " ").trim();
    const size = estimateText({ textContent: text, getAttribute: () => null, style: {} });
    const translate = parseTranslate(tag.match(/\btransform=["']([^"']+)["']/i)?.[1]);
    bounds = mergeBounds(bounds, {
      x: attr(tag, "x") + translate.x,
      y: attr(tag, "y") + translate.y - size.height,
      width: size.width,
      height: size.height,
    });
  }

  if (!bounds) return null;
  const padding = 16;
  return {
    x: Math.floor(bounds.x1 - padding),
    y: Math.floor(bounds.y1 - padding),
    width: Math.ceil(bounds.x2 - bounds.x1 + padding * 2),
    height: Math.ceil(bounds.y2 - bounds.y1 + padding * 2),
  };
}

function normalizeSvg(svg, args) {
  const declaredViewBox = parseViewBox(svg);
  const contentViewBox = computeContentViewBox(svg);
  const selectedViewBox =
    contentViewBox &&
    (!declaredViewBox ||
      contentViewBox.width > declaredViewBox.width * 1.1 ||
      contentViewBox.height > declaredViewBox.height * 1.1)
      ? contentViewBox
      : declaredViewBox;
  const viewBox = padViewBox(selectedViewBox);
  const width = Math.ceil(args.width ?? ((viewBox?.width ?? 800) * args.scale));
  const height = Math.ceil(args.height ?? ((viewBox?.height ?? 600) * args.scale));

  let normalized = injectFontCss(svg);
  if (viewBox) {
    normalized = setRootSvgAttr(normalized, "viewBox", `${viewBox.x} ${viewBox.y} ${viewBox.width} ${viewBox.height}`);
  }

  normalized = setRootSvgAttr(normalized, "width", width);
  normalized = setRootSvgAttr(normalized, "height", height);

  if (!rootSvgHasAttr(normalized, "xmlns", "http://www.w3.org/2000/svg")) {
    normalized = setRootSvgAttr(normalized, "xmlns", "http://www.w3.org/2000/svg");
  }

  normalized = injectBackgroundRect(normalized, args.background, viewBox, width, height);

  return { svg: normalized, width, height, viewBox };
}

function sanitizeSvgForResvg(svg) {
  if (!/\bclass=["'][^"']*\bclassDiagram\b/i.test(svg)) return svg;
  return svg
    .replace(/\smarker-(?:start|mid|end)=["'][^"']*["']/gi, "")
    .replace(/<g\b[^>]*\bclass=["'][^"']*\bdivider\b[^"']*["'][^>]*>[\s\S]*?<\/g>/gi, "");
}

async function inspectPngMetadata(outputPath) {
  const { imageSize } = await import("image-size");
  const buffer = fs.readFileSync(outputPath);
  const dimensions = imageSize(buffer);
  return {
    type: dimensions.type ?? "unknown",
    width: dimensions.width ?? 0,
    height: dimensions.height ?? 0,
    bytes: buffer.length,
  };
}

async function inspectPngPixels(outputPath) {
  const { PNG } = await import("pngjs");
  const png = PNG.sync.read(fs.readFileSync(outputPath));
  const totalPixels = png.width * png.height;
  const stride = Math.max(1, Math.floor(totalPixels / 120000));
  const colors = new Map();
  let sampledPixels = 0;
  let nonTransparentPixels = 0;
  let differentFromCornerPixels = 0;
  const corner = [
    png.data[0],
    png.data[1],
    png.data[2],
    png.data[3],
  ];

  for (let pixel = 0; pixel < totalPixels; pixel += stride) {
    const offset = pixel * 4;
    const rgba = [
      png.data[offset],
      png.data[offset + 1],
      png.data[offset + 2],
      png.data[offset + 3],
    ];
    sampledPixels += 1;
    if (rgba[3] > 8) nonTransparentPixels += 1;
    const diff =
      Math.abs(rgba[0] - corner[0]) +
      Math.abs(rgba[1] - corner[1]) +
      Math.abs(rgba[2] - corner[2]) +
      Math.abs(rgba[3] - corner[3]);
    if (diff > 12) differentFromCornerPixels += 1;
    const key = rgba.join(",");
    colors.set(key, (colors.get(key) ?? 0) + 1);
  }

  const dominantColorCount = Math.max(0, ...colors.values());
  return {
    total_pixels: totalPixels,
    sampled_pixels: sampledPixels,
    unique_colors: colors.size,
    non_transparent_pixels: nonTransparentPixels,
    different_from_corner_pixels: differentFromCornerPixels,
    non_transparent_ratio: nonTransparentPixels / sampledPixels,
    different_from_corner_ratio: differentFromCornerPixels / sampledPixels,
    dominant_color_ratio: dominantColorCount / sampledPixels,
  };
}

function metadataGate(metadata) {
  if (metadata.type !== "png") {
    return { status: "FAIL", message: `Expected PNG, got ${metadata.type}` };
  }
  if (metadata.bytes <= 0) {
    return { status: "FAIL", message: "PNG file is empty" };
  }
  if (metadata.width < 64 || metadata.height < 64) {
    return { status: "FAIL", message: `PNG is suspiciously small: ${metadata.width}x${metadata.height}` };
  }
  return { status: "PASS", message: `${metadata.width}x${metadata.height}, ${metadata.bytes} bytes` };
}

function pixelGate(pixelSanity) {
  if (pixelSanity.non_transparent_pixels === 0) {
    return { status: "FAIL", message: "PNG is fully transparent" };
  }
  if (pixelSanity.non_transparent_ratio < 0.995) {
    return { status: "FAIL", message: `PNG canvas has transparent areas: ${(pixelSanity.non_transparent_ratio * 100).toFixed(2)}% opaque` };
  }
  if (pixelSanity.unique_colors < 3) {
    return { status: "FAIL", message: `PNG has too few colors: ${pixelSanity.unique_colors}` };
  }
  if (pixelSanity.different_from_corner_ratio < 0.01) {
    return { status: "FAIL", message: `PNG differs from background in only ${(pixelSanity.different_from_corner_ratio * 100).toFixed(2)}% of sampled pixels` };
  }
  if (pixelSanity.dominant_color_ratio > 0.995) {
    return { status: "FAIL", message: `PNG is nearly one color: ${(pixelSanity.dominant_color_ratio * 100).toFixed(2)}% dominant` };
  }
  return {
    status: "PASS",
    message: `${pixelSanity.unique_colors} colors, ${(pixelSanity.different_from_corner_ratio * 100).toFixed(2)}% non-background sample`,
  };
}

async function renderMermaidToSvg(source, args) {
  const { JSDOM } = await import("jsdom");
  const dom = new JSDOM("<!doctype html><html><body><main id=\"root\"></main></body></html>", {
    pretendToBeVisual: true,
    url: "http://localhost/",
  });
  const restore = installDomGlobals(dom);

  try {
    const mermaidModule = await import("mermaid");
    const mermaid = mermaidModule.default ?? mermaidModule;
    mermaid.initialize({
      startOnLoad: false,
      theme: args.theme,
      look: "classic",
      fontFamily: "Noto Sans, sans-serif",
      securityLevel: "strict",
      htmlLabels: false,
      deterministicIds: true,
      deterministicIDSeed: "mermaid-skill",
      flowchart: { htmlLabels: false, useMaxWidth: false },
      class: { defaultRenderer: "dagre-wrapper", useMaxWidth: false },
      sequence: { useMaxWidth: false },
      gantt: { useMaxWidth: false },
      mindmap: { useMaxWidth: false },
    });

    await mermaid.parse(source, { suppressErrors: false });
    const container = dom.window.document.getElementById("root");
    const id = "mermaid-skill-diagram";
    const rendered = await mermaid.render(id, source, container);
    return rendered.svg;
  } finally {
    restore();
  }
}

async function renderSvgToPng(svg, args, outputPath, svgOutputPath = null) {
  const { Resvg } = await import("@resvg/resvg-js");
  const normalized = normalizeSvg(svg, args);
  normalized.svg = sanitizeSvgForResvg(normalized.svg);
  if (svgOutputPath) fs.writeFileSync(svgOutputPath, normalized.svg, "utf8");
  const options = {
    fitTo: {
      mode: "width",
      value: normalized.width,
    },
    font: {
      fontBuffers: fontBuffers(),
      loadSystemFonts: false,
      defaultFontFamily: "Noto Sans",
    },
  };
  if (args.background !== "transparent") {
    options.background = args.background;
  }

  const resvg = new Resvg(normalized.svg, options);
  const png = resvg.render().asPng();
  fs.writeFileSync(outputPath, png);
  return normalized;
}

async function ensureDependencies(args) {
  let dependencies = await checkDependencies();
  let installResult = null;
  if (!dependencies.ok && args.install) {
    installResult = installLocalRenderer();
    dependencies = await checkDependencies();
  }
  return { dependencies, installResult };
}

async function main() {
  let args;
  try {
    args = parseArgs(process.argv.slice(2));
  } catch (error) {
    emit({ ok: false, message: error.message }, false);
    return 2;
  }

  if (args.help) {
    process.stdout.write(`${usage()}\n`);
    return 0;
  }

  const { dependencies, installResult } = await ensureDependencies(args);
  const installCommand = `cd ${shellQuote(SKILL_DIR)} && npm install --omit=dev --no-audit --fund=false`;

  if (args.checkTools) {
    emit(
      {
        ok: dependencies.ok,
        message: dependencies.ok ? "Sandbox-safe Node renderer available" : "Local Node renderer dependencies missing",
        renderer: dependencies.ok ? RENDERER_LABEL : null,
        required_packages: REQUIRED_PACKAGES,
        missing_packages: dependencies.missing,
        package_json: PACKAGE_JSON,
        install_attempted: args.install,
        install_result: installResult,
        install_command: installCommand,
      },
      args.json,
    );
    return 0;
  }

  if (!dependencies.ok) {
    emit(
      {
        ok: false,
        message: "Local Node renderer dependencies missing. Rerun with --install when dependency installation is allowed.",
        renderer: null,
        required_packages: REQUIRED_PACKAGES,
        missing_packages: dependencies.missing,
        package_json: PACKAGE_JSON,
        install_command: installCommand,
        install_attempted: args.install,
        install_result: installResult,
      },
      args.json,
    );
    return 3;
  }

  let inputPath;
  let outputPath;
  let svgOutputPath;
  try {
    ({ inputPath, outputPath, svgOutputPath } = validateRenderArgs(args));
  } catch (error) {
    emit({ ok: false, message: error.message }, args.json);
    return 2;
  }

  const tempDir = fs.mkdtempSync(path.join(os.tmpdir(), "mermaid-render-"));
  try {
    const source = prepareInput(inputPath, tempDir);
    const svg = await renderMermaidToSvg(source, args);
    const normalized = await renderSvgToPng(svg, args, outputPath, svgOutputPath);

    if (!fs.existsSync(outputPath) || fs.statSync(outputPath).size <= 0) {
      throw new Error("Render finished, but PNG output is missing or empty.");
    }

    const metadata = await inspectPngMetadata(outputPath);
    const pixelSanity = await inspectPngPixels(outputPath);
    const pngMetadataGate = metadataGate(metadata);
    const pngPixelGate = pixelGate(pixelSanity);
    const gates = {
      source: { status: "PASS", message: "Mermaid source parsed successfully" },
      render: { status: "PASS", message: "SVG rendered and converted to PNG without Chromium" },
      png_metadata: pngMetadataGate,
      png_pixel: pngPixelGate,
      visual: {
        status: "REQUIRED",
        message: "Open the generated PNG directly as an image and run VLM visual review before delivery.",
      },
    };
    const ok = pngMetadataGate.status === "PASS" && pngPixelGate.status === "PASS";
    const payload = {
      ok,
      message: ok ? "PNG rendered and technical gates passed; VLM visual review still required" : "PNG rendered, but a technical gate failed",
      renderer: RENDERER_LABEL,
      input: inputPath,
      output: outputPath,
      svg_output: svgOutputPath,
      bytes: metadata.bytes,
      width: metadata.width,
      height: metadata.height,
      metadata,
      pixel_sanity: pixelSanity,
      gates,
      required_next_action: "Open output PNG directly and perform visual review with the language model.",
    };
    const schema = await getProtocolSchema();
    emitProtocol(payload, args.json, schema);
    return ok ? 0 : 4;
  } catch (error) {
    emit({
      ok: false,
      message: error.message,
      renderer: RENDERER_LABEL,
      gates: {
        source: { status: "FAIL", message: "Render pipeline failed before all technical gates completed" },
        render: { status: "FAIL", message: error.message },
      },
      stack: error.stack,
    }, args.json);
    return 1;
  } finally {
    fs.rmSync(tempDir, { recursive: true, force: true });
  }
}

process.exitCode = await main();

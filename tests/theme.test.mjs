import { test } from "node:test";
import assert from "node:assert/strict";
import { readFileSync, existsSync } from "node:fs";
import { runInNewContext } from "node:vm";
import { fileURLToPath } from "node:url";
import { resolve } from "node:path";
const root = fileURLToPath(new URL("../", import.meta.url));
const read = p => readFileSync(resolve(root, p), "utf8");
const manifest = JSON.parse(read("manifest.json"));
const context = {};
runInNewContext(read("palette.js") + read("theme.js"), context);
const palette = context.EVERFOREST_PALETTE;
const theme = context.buildEverforestTheme(palette);
const expected = {
  bg_dim: "#232a2e", bg0: "#2d353b", bg1: "#343f44", bg2: "#3d484d",
  bg3: "#475258", bg4: "#4f585e", bg5: "#56635f", bg_visual: "#543a48",
  bg_red: "#514045", bg_yellow: "#4d4c43", bg_green: "#425047",
  bg_blue: "#3a515d", bg_purple: "#4a444e", fg: "#d3c6aa", red: "#e67e80",
  orange: "#e69875", yellow: "#dbbc7f", green: "#a7c080", aqua: "#83c092",
  blue: "#7fbbb3", purple: "#d699b6", grey0: "#7a8478", grey1: "#859289", grey2: "#9da9a0",
};

test("palette matches all 24 upstream dark-medium values and is immutable", () => {
  assert.deepEqual(JSON.parse(JSON.stringify(palette)), expected);
  assert.ok(Object.isFrozen(palette));
});
test("every theme colour comes from the canonical palette", () => {
  const values = new Set(Object.values(expected));
  for (const [key, value] of Object.entries(theme.colors)) assert.ok(values.has(value), key);
});
test("manifest experiment mapping covers every palette key", () => {
  assert.equal(Object.keys(manifest.theme_experiment.colors).length, 24);
  for (const key of Object.keys(expected)) {
    assert.equal(manifest.theme_experiment.colors[`everforest_${key}`], `--ef-${key.replaceAll("_", "-")}`);
    assert.equal(theme.colors[`everforest_${key}`], expected[key]);
  }
});
test("theme remains dark irrespective of system mode, without polling", () => {
  assert.equal(theme.properties.color_scheme, "dark");
  assert.equal(theme.properties.content_color_scheme, "dark");
  assert.doesNotMatch(read("background.js"), /matchMedia|setInterval/);
});
test("runtime references exist and extension ID is retained for upgrades", () => {
  assert.equal(manifest.browser_specific_settings.gecko.id, "everforest-night@jarith");
  assert.equal(manifest.browser_specific_settings.gecko.strict_min_version, "149.0");
  assert.equal(manifest.browser_specific_settings.gecko.strict_max_version, "170.0");
  for (const file of [...manifest.background.scripts, ...Object.values(manifest.icons),
    manifest.theme_experiment.stylesheet, "content.css", "compose.css", "palette.css"]) {
    assert.ok(existsSync(resolve(root, file)), file);
  }
  assert.deepEqual(manifest.permissions, ["theme", "messagesRead", "compose", "scripting"]);
});
test("no literal colours outside the shared generated palette", () => {
  for (const path of ["theme.js", "background.js", "chrome.css", "content.css", "compose.css"]) {
    assert.doesNotMatch(read(path), /#[a-f\d]{3,8}\b|rgba?\(|hsla?\(/i, path);
  }
});
test("screen styles preserve print and forced-colour accessibility", () => {
  for (const path of ["chrome.css", "content.css", "compose.css"]) {
    assert.match(read(path), /@media screen and \(not \(forced-colors: active\)\)/, path);
  }
});
test("HTML reader styling stays scoped and never edits the compose DOM", () => {
  assert.match(read("content.css"), /body > :is\(\.moz-text-plain, \.moz-text-flowed, \.moz-text-html\)/);
  assert.doesNotMatch(read("content.css"), /\*\s*\{/);
  assert.match(read("compose.css"), /body:not\(\[bgcolor\]\):not\(\[text\]\)/);
  assert.doesNotMatch(read("background.js"), /executeScript|setAttribute|fetch\(/);
});

async function boot({ registered = false, fail = false } = {}) {
  const calls = [], errors = [];
  const api = name => ({
    async getRegisteredScripts() { return registered ? [{ id: "existing" }] : []; },
    async registerScripts(scripts) {
      calls.push({ name, scripts });
      if (fail && name === "messageDisplay") throw Error("test registration failure");
    },
  });
  const sandbox = { ...context, console: { error: (...args) => errors.push(args) },
    messenger: { theme: { async update(t) { calls.push({ name: "theme", theme: t }); } },
      scripting: { messageDisplay: api("messageDisplay"), compose: api("compose") } } };
  runInNewContext(read("background.js"), sandbox);
  await new Promise(resolve => setImmediate(resolve));
  return { calls, errors };
}
test("startup registers palette before separate reader and compose styles", async () => {
  const { calls, errors } = await boot();
  assert.equal(errors.length, 0);
  assert.deepEqual(calls.map(c => c.name), ["theme", "messageDisplay", "compose"]);
  assert.equal(calls[1].scripts[0].css.join(), "palette.css,content.css");
  assert.equal(calls[2].scripts[0].css.join(), "palette.css,compose.css");
});
test("existing registrations do not cause duplicate-ID failures", async () => {
  const { calls } = await boot({ registered: true });
  assert.equal(calls.length, 1);
});
test("registration errors are reported without blocking other surfaces", async () => {
  const { calls, errors } = await boot({ fail: true });
  assert.equal(calls.length, 3);
  assert.equal(errors.length, 1);
  assert.match(errors[0][0], /message styles/);
});


test("legacy tree/card/folder tokens use the palette, including inactive selections", () => {
  for (const token of ["tree-pane-background", "tree-card-background-selected-unfocused",
    "tree-card-background-selected-current-unfocused", "listbox-color", "sidebar-background",
    "folder-color-inbox", "folder-color-draft", "folderpane-unread-count-text"]) {
    assert.ok(read("chrome.css").includes(`--${token}: var(--ef-`), token);
  }
  assert.match(read("chrome.css"), /#threadTree \{[\s\S]*?background-color: var\(--ef-bg0\) !important/);
  assert.match(read("chrome.css"), /--read-status-fill: var\(--ef-green\) !important/);
});

test("HTML mail has presentation-only palette overrides without recolouring media", () => {
  const css = read("content.css");
  assert.match(css, /\.moz-text-html :is\(div/);
  assert.match(css, /a:any-link/);
  assert.doesNotMatch(css, /(?:^|,)\s*(?:img|svg|video|canvas)\b/m);
  assert.doesNotMatch(css, /filter:|background-image:|display:|position:/);
  assert.doesNotMatch(read("compose.css"), /moz-text-html/);
});

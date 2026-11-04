const DARK = {
  bg0: "#272f34",
  bg1: "#2c353a",
  bg: "#323d43",
  bg2: "#3c474d",
  bg4: "#505a60",
  bg5: "#576268",
  grey0: "#b1b6ad",
  grey2: "#b0bab0",
  fg: "#d8caac",
  red: "#eda0a1",
  green: "#a7c080",
  aqua: "#83c092",
};

const LIGHT = {
  bg0: "#e5dcc0",
  bg1: "#ede3c8",
  bg: "#f3ebd2",
  bg2: "#ded4bb",
  bg4: "#c3b9a0",
  bg5: "#b2a88f",
  grey0: "#5a6358",
  grey2: "#495247",
  fg: "#4f5b62",
  red: "#ad3b4a",
  green: "#47661b",
  aqua: "#2c7459",
};

const buildTheme = (palette, isDark) => {
  return {
    colors: {
      frame: palette.bg0,
      frame_inactive: palette.bg0,

      toolbar: palette.bg,
      toolbar_text: palette.grey2,
      toolbar_top_separator: palette.bg0,
      toolbar_bottom_separator: palette.bg,
      toolbar_vertical_separator: palette.bg5,

      toolbar_field: palette.bg1,
      toolbar_field_text: palette.fg,
      toolbar_field_border: palette.bg5,
      toolbar_field_focus: palette.bg1,
      toolbar_field_text_focus: palette.fg,
      toolbar_field_border_focus: palette.green,
      toolbar_field_highlight: palette.bg4,
      toolbar_field_highlight_text: palette.fg,

      tab_selected: palette.bg,
      tab_text: palette.fg,
      tab_background_text: palette.grey0,
      tab_background_separator: palette.bg,
      tab_line: palette.green,
      tab_loading: palette.aqua,

      button_background_hover: palette.bg2,
      button_background_active: palette.bg4,

      icons: palette.aqua,
      icons_attention: palette.red,

      sidebar: palette.bg,
      sidebar_text: palette.grey2,
      sidebar_border: palette.bg0,
      sidebar_highlight: palette.bg4,
      sidebar_highlight_text: palette.fg,
      sidebar_highlight_border: palette.bg4,

      badge_bg: palette.green,
      badge_text: isDark ? DARK.bg0 : LIGHT.bg,

      tree_view_bg: palette.bg,
      tree_view_color: palette.grey2,
      spaces_bg: palette.bg0,
      new_folder_color: palette.green,

      popup: palette.bg1,
      popup_text: palette.grey2,
      popup_border: palette.bg5,
      popup_highlight: palette.bg2,
      popup_highlight_text: palette.fg,
    },
    properties: {
      color_scheme: "auto",
      content_color_scheme: isDark ? "dark" : "light",
    },
  };
}

const applyTheme = (isDark) => {
  const palette = isDark ? DARK : LIGHT;
  messenger.theme.update(buildTheme(palette, isDark));
}

const mql = window.matchMedia("(prefers-color-scheme: dark)");

mql.addEventListener("change", (e) => applyTheme(e.matches));

let lastIsDark = mql.matches;
applyTheme(lastIsDark);

// Polling fallback: matchMedia change events may not fire reliably
// in Thunderbird extension background pages (Bug 1741009)
setInterval(() => {
  const isDark = mql.matches;
  if (isDark !== lastIsDark) {
    lastIsDark = isDark;
    applyTheme(isDark);
  }
}, 2000);

messenger.scripting.messageDisplay.registerScripts([
  { id: "everforest-message-display", css: ["content.css"] },
]);

messenger.scripting.compose.registerScripts([
  { id: "everforest-compose", css: ["content.css"] },
]);

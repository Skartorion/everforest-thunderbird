/* Use documented theme keys first; theme_experiment supplies the remaining UI. */
globalThis.buildEverforestTheme = (p) => ({
  colors: {
    frame: p.bg_dim, frame_inactive: p.bg_dim,
    toolbar: p.bg0, toolbar_text: p.fg,
    toolbar_top_separator: p.bg_dim, toolbar_bottom_separator: p.bg4,
    toolbar_vertical_separator: p.bg4,
    toolbar_field: p.bg1, toolbar_field_text: p.fg,
    toolbar_field_border: p.bg4, toolbar_field_focus: p.bg0,
    toolbar_field_text_focus: p.fg, toolbar_field_border_focus: p.green,
    toolbar_field_highlight: p.bg_visual, toolbar_field_highlight_text: p.fg,
    tab_selected: p.bg1, tab_text: p.fg, tab_background_text: p.grey2,
    tab_background_separator: p.bg4, tab_line: p.green, tab_loading: p.aqua,
    button_background_hover: p.bg2, button_background_active: p.bg3,
    icons: p.fg, icons_attention: p.yellow,
    sidebar: p.bg1, sidebar_text: p.fg, sidebar_border: p.bg4,
    sidebar_highlight: p.bg_green, sidebar_highlight_text: p.fg,
    sidebar_highlight_border: p.green,
    popup: p.bg2, popup_text: p.fg, popup_border: p.bg4,
    popup_highlight: p.green, popup_highlight_text: p.bg0,
    ...Object.fromEntries(Object.entries(p).map(([key, value]) => [
      `everforest_${key}`, value,
    ])),
  },
  properties: { color_scheme: "dark", content_color_scheme: "dark" },
});

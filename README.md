# Everforest Dark Medium for Thunderbird

A consistently dark Thunderbird theme using the **exact Everforest Dark Medium**
palette from [sainnhe/everforest](https://github.com/sainnhe/everforest/blob/master/palette.md).
No automatic light-mode switch or approximate/legacy Everforest colours.

## Compatibility

Targets **Thunderbird 159.x**, the latest stable release verified on 2026-11-04.
The extension is intentionally limited to `159.*`: experiment CSS relies on
Thunderbird internals, so new major releases need a compatibility check, not a
speculative compatibility claim. ESR, beta and nightly are not currently targets.

The original `everforest-night@jarith` extension ID is retained so an existing
installation can be upgraded. The display name and project metadata identify
this fork; the original author is credited below.

## Coverage

- Application frame, tabs, unified toolbar, search fields, menus and popups.
- Spaces toolbar, folder pane, unread badges, message table and message cards.
- Hover, selected, focused, unread, starred and junk states.
- Layout/semantic colour tokens used by theme-aware settings and other UI pages.
- Message header, attachment/compose containers and notification bars.
- Plain-text/flowed message backgrounds, links, quotations and text selection.
- Compose editor default surface, caret and selection, without editing message HTML.

Default background is `#2d353b`, pane/card background is `#343f44`, foreground is
`#d3c6aa`, and the primary accent is `#a7c080`. All colour literals live in
`palette.js` and its generated `palette.css` counterpart.

## Install

1. Download the `everforest-dark-medium` artifact from a successful **Validate and package** run on the repository's Actions page, or build the XPI locally below.
2. Extract the artifact ZIP to obtain `everforest-dark-medium-3.0.0.xpi`.
3. Open Thunderbird's **Add-ons and Themes**, use the gear menu, and choose **Install Add-on From File**; select the XPI.
4. Reopen already displayed messages and compose windows after enabling or updating the add-on. Registration applies to newly opened messages/editors.

For development, open **Add-ons and Themes → Extensions → gear → Debug Add-ons**,
choose **Load Temporary Add-on**, and select `manifest.json`. A temporary add-on
is removed on restart. Do not enable another theme at the same time.

## Build and test

Requires Node.js 20+ and Python 3; no npm dependencies or installation step.

```sh
npm run generate  # regenerate palette.css after changing palette.js
npm test          # palette, manifest, API/lifecycle and safety checks
npm run build     # checks + reproducible XPI under dist/
```

CI runs these checks for pushes and pull requests, then publishes the XPI as a
workflow artifact. Only runtime files and existing icons are included in the XPI;
tests, automation fixtures, development metadata and repository data are excluded.

See [TESTING.md](TESTING.md) for the verified runtime checks and remaining manual
checks, including a disposable-profile integration test.

## Intentional boundaries

Sender-designed HTML emails, images, signatures and explicit compose colours are
not globally recoloured. Use Thunderbird's built-in dark-message toggle for HTML
mail; it can independently change the rendered message. Custom folder/tag and
calendar colours are not forcibly replaced. Native operating-system decorations
and file pickers may keep their own appearance. This is not a promise to recolour
every third-party page or component.

Experiment styles apply only to screen media outside forced-colour mode; printing
is not restyled. No universal `*` repaint or destructive HTML rewriting is used.
The extension does not set Thunderbird preferences, contact remote servers, read
message bodies in JavaScript, or send mail. Native APIs handle extension/theme
removal; there is no persistent userChrome.css or profile preference to clean up.

## Permissions

`theme` applies the application colours. `scripting` plus `messagesRead` and
`compose` allow Thunderbird to inject presentation-only CSS into message readers
and editors. These are API-required capabilities, not permission-free theming;
the implementation registers CSS only and contains no message-reading or sending
logic. No host/network permissions are requested.

## Architecture and references

`palette.js` is the source of truth. `theme.js` builds the documented theme API
colours; `theme_experiment` maps the palette into additional application UI CSS.
`content.css` and `compose.css` are separate so reader-only selectors cannot leak
into outgoing-message editing. Startup operations report errors independently and
skip existing script IDs; no OS-theme polling is needed.

- [Thunderbird theme API and theme_experiment](https://webextension-api.thunderbird.net/en/mv2/theme.html)
- [Message display scripting](https://webextension-api.thunderbird.net/en/mv2/scripting.messageDisplay.html)
- [Compose scripting](https://webextension-api.thunderbird.net/en/mv2/scripting.compose.html)
- [Supported manifest keys](https://developer.thunderbird.net/add-ons/mailextensions/supported-manifest-keys)
- [Official release metadata](https://product-details.mozilla.org/1.0/thunderbird_versions.json)

Manifest V2 is retained deliberately: Thunderbird supports it and this is a small
persistent-background add-on, not a browser service-worker migration.

## Attribution

Based on the repository's original **Everforest Night** implementation by
[jarith](https://github.com/jarith/everforest-night-thunderbird).
Palette design by [sainnhe and Everforest contributors](https://github.com/sainnhe/everforest).
Existing icons and original attribution are retained. No new repository-wide
license is asserted for inherited assets.

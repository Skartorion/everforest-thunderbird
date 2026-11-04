# Validation

## Verified on 2026-11-04

- Node.js 20: all 11 automated tests pass (`npm test`).
- Reproducible XPI packaging: build contains only declared runtime files and icons.
- Linux x86-64, Thunderbird 159.0 from Mozilla's official release distribution,
  fresh disposable profile under Xvfb; no real account or mail data.
- Live checks: temporary installation; folder palette propagation; card foreground
  and background; selected cards; plain-text reader CSS injection; table view
  background; authored HTML colour preservation with Thunderbird's own dark-message
  conversion disabled; compose injection; no outgoing body colour attributes; and
  removal of the application stylesheet on uninstall.

The integration check is in `tests/thunderbird_smoke.py`. It creates local-only
`example.invalid` fixtures and an identity. **Never run it on a real profile**.
It opens a compose window but never sends mail. It uninstalls this add-on at the
end so application-theme cleanup is explicitly checked.

```sh
python3 -m pip install marionette_driver
# Start a dedicated disposable profile with a local-folder account:
MOZ_REMOTE_ALLOW_SYSTEM_ACCESS=1 thunderbird --no-remote \
  --profile /absolute/path/to/disposable-profile --marionette
python3 tests/thunderbird_smoke.py
```

The profile must have a Local Folders account and Marionette on its default port
2828. This is an optional local integration test, not part of the dependency-free
Node CI suite. Temporary add-on installation does not test persistence on restart.

## Manual release checklist

- Windows and macOS (including native menus/title bars), HiDPI and all UI densities.
- Persistent XPI install, full restart, disable/re-enable and upgrade from 2.0.0.
- Folder hover/selected/unfocused states, unread/new mail, starred/junk icons.
- Card/table sorting, grouped/collapsed threads and keyboard focus visibility.
- Global search, quick filter, context menus, settings, address book and calendar.
- Message header, attachments and informational/warning/error notifications.
- Plain-text/flowed mail, nested quotations, links, selection and print preview.
- HTML mail with built-in dark-message mode both on and off.
- HTML compose, custom body colours, signatures, quoted replies and draft round-trip.
- Forced-colour accessibility and large text.

Automated coverage is not a claim that every page/control has been visually
verified on every platform. Third-party content, OS dialogs, sender-authored HTML
and user-defined tag/calendar colours are intentional boundaries.

/* Registration applies to newly opened messages/editors (Thunderbird API).
 * Stylesheets only: never read message contents or change outgoing HTML. */
async function registerStyles(api, id, css) {
  const registered = await api.getRegisteredScripts({ ids: [id] });
  if (!registered.length) {
    await api.registerScripts([{ id, css }]);
  }
}

async function startEverforest() {
  // Independent operations: a failure in one must not prevent the others.
  const results = await Promise.allSettled([
    messenger.theme.update(buildEverforestTheme(EVERFOREST_PALETTE)),
    registerStyles(messenger.scripting.messageDisplay,
      "everforest-message-display", ["palette.css", "content.css"]),
    registerStyles(messenger.scripting.compose,
      "everforest-compose", ["palette.css", "compose.css"]),
  ]);
  const labels = ["application theme", "message styles", "compose styles"];
  results.forEach((result, index) => {
    if (result.status === "rejected") {
      console.error(`Everforest: could not apply ${labels[index]}`, result.reason);
    }
  });
}

// No preference writes, polling, OS-light-mode fallback or remote requests.
startEverforest().catch(error => console.error("Everforest startup failed", error));

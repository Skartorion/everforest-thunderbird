"""Run against a DISPOSABLE, Marionette-enabled Thunderbird 159 profile only.

Requires `pip install marionette_driver`. Start with --marionette and
MOZ_REMOTE_ALLOW_SYSTEM_ACCESS=1. Creates local example.invalid fixtures and an
identity; never connects to a mail account or sends a message.
"""
from pathlib import Path
import json
import time
from marionette_driver.marionette import Marionette

root = Path(__file__).resolve().parent.parent
client = Marionette()
client.start_session()
client.set_context("chrome")
client.timeout.script = 30
checks = []


def js(script, *args):
    return client.execute_script(script, script_args=list(args))


def wait(script, timeout=15):
    end = time.monotonic() + timeout
    while time.monotonic() < end:
        value = js(script)
        if value:
            return value
        time.sleep(0.1)
    raise AssertionError(f"Timed out: {script}")


pane = "const p=Services.wm.getMostRecentWindow('mail:3pane').document.getElementById('tabmail').tabInfo[0].chromeBrowser.contentWindow;"
message = "const w=Services.wm.getMostRecentWindow('mail:3pane');const a=w.document.getElementById('tabmail').currentAboutMessage;const b=a?.document.getElementById('messagepane');"
try:
    version = js("return Services.appinfo.version;")
    assert version.startswith("159."), version
    install = client.execute_async_script("""
      const done=arguments[arguments.length-1];
      const {AddonManager}=ChromeUtils.importESModule('resource://gre/modules/AddonManager.sys.mjs');
      const f=Cc['@mozilla.org/file/local;1'].createInstance(Ci.nsIFile);
      f.initWithPath(arguments[0]);
      AddonManager.installTemporaryAddon(f).then(a=>done({id:a.id}),e=>done({error:e.message}));
    """, script_args=[str(root)])
    assert install.get("id") == "everforest-night@jarith", install
    wait(pane + "return p.getComputedStyle(p.document.getElementById('folderPane')).backgroundColor==='rgb(52, 63, 68)';")
    checks += ["temporary installation", "folder pane palette propagation"]
    js(r"""
      const {MailServices}=ChromeUtils.importESModule('resource:///modules/MailServices.sys.mjs');
      const root=MailServices.accounts.localFoldersServer.rootFolder;
      const name='Everforest smoke '+Date.now();root.createSubfolder(name,null);
      const f=root.getChildNamed(name).QueryInterface(Ci.nsIMsgLocalMailFolder);
      for(let i=0;i<3;i++) {
        const body=i===2?'<html><body><div id="authored" style="background-color:rgb(240, 240, 240);color:rgb(20, 20, 20)">HTML fixture</div></body></html>':'Plain text fixture.\r\nhttps://example.invalid/\r\n> Quoted text';
        f.addMessage(['From: Test Sender <sender@example.invalid>',
          'To: Test Reader <reader@example.invalid>','Date: Thu, 01 Jan 2026 10:00:00 +0000',
          'Subject: Everforest smoke '+i,'Message-ID: <'+Date.now()+'-'+i+'@example.invalid>',
          'MIME-Version: 1.0','Content-Type: '+(i===2?'text/html':'text/plain')+'; charset=UTF-8',
          '',body,''].join('\r\n'));
      }
      const t=Services.wm.getMostRecentWindow('mail:3pane').document.getElementById('tabmail');
      t.switchToTab(0);t.currentAbout3Pane.displayFolder(f);
      Services.prefs.setIntPref('mail.threadpane.listview',0);
      t.currentAbout3Pane.threadPane.updateThreadView();return true;
    """)
    wait(pane + "return p.document.querySelectorAll('.card-container').length===3;")
    cards = js(pane + "return [...p.document.querySelectorAll('.card-container')].map(e=>({bg:p.getComputedStyle(e).backgroundColor,fg:p.getComputedStyle(e).color}));")
    assert all(c == {"bg": "rgb(52, 63, 68)", "fg": "rgb(211, 198, 170)"} for c in cards), cards
    checks += ["card background and foreground"]
    js(pane + "p.threadTree.selectedIndex=1;p.threadTree.table.body.focus();return true;")
    wait(pane + "const e=p.document.querySelector('.card-layout.selected .card-container');return e && p.getComputedStyle(e).backgroundColor==='rgb(66, 80, 71)';")
    wait(message + "return !!b?.contentDocument?.querySelector('.moz-text-plain');")
    wait(message + "return b.contentWindow.getComputedStyle(b.contentDocument.body).backgroundColor==='rgb(45, 53, 59)';")
    checks += ["selected cards", "plain-text reader CSS injection"]
    js(pane + "Services.prefs.setIntPref('mail.threadpane.listview',1);p.threadPane.updateThreadView();return true;")
    wait(pane + "return p.threadTree.getAttribute('rows')==='thread-row' && p.getComputedStyle(p.threadTree).backgroundColor==='rgb(45, 53, 59)';")
    checks += ["table view background"]
    js(pane + "p.threadTree.selectedIndex=2;return true;")
    wait(message + "return !!b?.contentDocument?.querySelector('#authored');")
    js(message + "const toggle=a.document.getElementById('disableDarkReader');if(!toggle.checked)toggle.click();return true;")
    wait(message + "const e=b?.contentDocument?.querySelector('#authored');return e?.style.backgroundColor==='rgb(240, 240, 240)';")
    html = js(message + "const e=b.contentDocument.querySelector('#authored');return {bg:e.style.backgroundColor,fg:e.style.color};")
    assert html == {"bg": "rgb(240, 240, 240)", "fg": "rgb(20, 20, 20)"}, html
    # Our reader stylesheet must not match an HTML body (TB may transform its
    # computed colours independently through its built-in dark message feature).
    assert not js(message + "return b.contentDocument.body.matches('body:has(> :is(.moz-text-plain, .moz-text-flowed))');")
    checks += ["authored HTML styles and selector isolation"]
    js(r"""
      const {MailServices}=ChromeUtils.importESModule('resource:///modules/MailServices.sys.mjs');
      const account=MailServices.accounts.accounts[0];let identity=account.defaultIdentity;
      if(!identity){identity=MailServices.accounts.createIdentity();identity.email='test@example.invalid';account.addIdentity(identity);account.defaultIdentity=identity;}
      const params=Cc['@mozilla.org/messengercompose/composeparams;1'].createInstance(Ci.nsIMsgComposeParams);
      params.type=Ci.nsIMsgCompType.New;params.format=Ci.nsIMsgCompFormat.PlainText;
      params.identity=identity;params.composeFields=Cc['@mozilla.org/messengercompose/composefields;1'].createInstance(Ci.nsIMsgCompFields);
      MailServices.compose.OpenComposeWindowWithParams(null,params);return true;
    """)
    compose = "const w=Services.wm.getMostRecentWindow('msgcompose');const e=w?.GetCurrentEditorElement();"
    wait(compose + "return e?.contentDocument?.body && e.contentWindow.getComputedStyle(e.contentDocument.body).backgroundColor==='rgb(45, 53, 59)';")
    attrs = js(compose + "return [...e.contentDocument.body.attributes].map(a=>[a.name,a.value]);")
    assert all(name not in ("bgcolor", "text") for name, _ in attrs), attrs
    assert not any("color" in value.lower() for name, value in attrs if name == "style"), attrs
    checks += ["compose editor injection", "no outgoing body colour attributes"]
    # Ensure uninstall removes the experiment stylesheet from application UI.
    removed = client.execute_async_script("""
      const done=arguments[arguments.length-1];
      const {AddonManager}=ChromeUtils.importESModule('resource://gre/modules/AddonManager.sys.mjs');
      AddonManager.getAddonByID('everforest-night@jarith').then(a=>a.uninstall()).then(()=>done(true),e=>done({error:e.message}));
    """)
    assert removed is True, removed
    wait(pane + "return !p.getComputedStyle(p.document.documentElement).getPropertyValue('--ef-bg0').trim();")
    checks += ["uninstall removes application stylesheet"]
    print(json.dumps({"thunderbird": version, "checks": checks}, indent=2))
finally:
    client.delete_session()

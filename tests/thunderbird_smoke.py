"""Run against a DISPOSABLE, Marionette-enabled Thunderbird 149/159 profile only.

Requires `pip install marionette_driver`. Start with --marionette and
MOZ_REMOTE_ALLOW_SYSTEM_ACCESS=1. Creates local example.invalid fixtures and an
identity; never connects to a mail account or sends a message.
"""
from pathlib import Path
import json
import os
import time
from marionette_driver.marionette import Marionette

root = Path(__file__).resolve().parent.parent
client = Marionette(port=int(os.environ.get("MARIONETTE_PORT", "2828")))
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
    assert int(version.split(".")[0]) >= 149, version
    install = client.execute_async_script("""
      const done=arguments[arguments.length-1];
      const {AddonManager}=ChromeUtils.importESModule('resource://gre/modules/AddonManager.sys.mjs');
      const f=Cc['@mozilla.org/file/local;1'].createInstance(Ci.nsIFile);
      f.initWithPath(arguments[0]);
      AddonManager.installTemporaryAddon(f).then(a=>done({id:a.id}),e=>done({error:e.message}));
    """, script_args=[os.environ.get("XPI_PATH", str(root))])
    assert install.get("id") == "everforest-night@jarith", install
    wait(pane + "return p.getComputedStyle(p.document.getElementById('folderPane')).backgroundColor==='rgb(52, 63, 68)';")
    checks += ["temporary installation", "folder pane palette propagation"]
    js(r"""
      const {MailServices}=ChromeUtils.importESModule('resource:///modules/MailServices.sys.mjs');
      const root=MailServices.accounts.localFoldersServer.rootFolder;
      const name='Everforest smoke '+Date.now();root.createSubfolder(name,null);
      const f=root.getChildNamed(name).QueryInterface(Ci.nsIMsgLocalMailFolder);
      for(let i=0;i<3;i++) {
        const body=i===2?'<html><body><div id="authored" style="background-color:rgb(240, 240, 240);color:rgb(20, 20, 20)">HTML fixture <a id="fixture-link" href="https://example.invalid/" style="color:red"><span>Link</span></a><img id="fixture-image" src="data:image/gif;base64,R0lGODlhAQABAIAAAAAAAP///yH5BAEAAAAALAAAAAABAAEAAAIBRAA7" width="1" height="1"></div></body></html>':'Plain text fixture.\r\nhttps://example.invalid/\r\n> Quoted text';
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
    tokens = js(pane + "const s=p.getComputedStyle(p.document.documentElement);return ['--folder-color-inbox','--folder-color-draft','--folder-color-spam'].map(k=>s.getPropertyValue(k).trim());")
    assert tokens == ["rgb(127, 187, 179)", "rgb(214, 153, 182)", "rgb(230, 126, 128)"], tokens
    checks += ["legacy folder icon palette defaults"]
    text = js(pane + "return [...p.document.querySelectorAll('.sender, .subject')].map(e=>p.getComputedStyle(e).color);")
    assert all(c == "rgb(211, 198, 170)" for c in text), text
    checks += ["card sender and subject palette"]
    js(pane + "p.threadTree.selectedIndex=1;p.threadTree.table.body.focus();return true;")
    wait(pane + "const e=p.document.querySelector('.card-layout.selected .card-container');return e && p.getComputedStyle(e).backgroundColor==='rgb(66, 80, 71)';")
    wait(message + "return !!b?.contentDocument?.querySelector('.moz-text-plain');")
    wait(message + "return b.contentWindow.getComputedStyle(b.contentDocument.body).backgroundColor==='rgb(45, 53, 59)';")
    checks += ["selected cards", "plain-text reader CSS injection"]
    js(pane + "Services.wm.getMostRecentWindow('mail:3pane').document.getElementById('button-appmenu').focus();return true;")
    wait(pane + "const e=p.document.querySelector('.card-layout.selected .card-container');return e && p.getComputedStyle(e).backgroundColor==='rgb(66, 80, 71)';")
    checks += ["selected card retains palette without focus"]
    js(pane + "Services.prefs.setIntPref('mail.threadpane.listview',1);p.threadPane.updateThreadView();return true;")
    wait(pane + "return p.threadTree.getAttribute('rows')==='thread-row' && p.getComputedStyle(p.threadTree).backgroundColor==='rgb(45, 53, 59)';")
    checks += ["table view background"]
    js(pane + "p.threadTree.selectedIndex=2;return true;")
    wait(message + "return !!b?.contentDocument?.querySelector('#authored');")
    js(message + "const toggle=a.document.getElementById('disableDarkReader');if(!toggle.checked)toggle.click();return true;")
    wait(message + "const e=b?.contentDocument?.querySelector('#authored');return e?.style.backgroundColor==='rgb(240, 240, 240)';")
    html = js(message + "const e=b.contentDocument.querySelector('#authored');return {bg:e.style.backgroundColor,fg:e.style.color};")
    assert html == {"bg": "rgb(240, 240, 240)", "fg": "rgb(20, 20, 20)"}, html
    # Presentation changes, but inline sender data and media remain unchanged.
    wait(message + "const e=b.contentDocument.querySelector('#authored');return b.contentWindow.getComputedStyle(e).backgroundColor==='rgb(45, 53, 59)' && b.contentWindow.getComputedStyle(e).color==='rgb(211, 198, 170)';")
    wait(message + "return b.contentWindow.getComputedStyle(b.contentDocument.querySelector('#fixture-link span')).color==='rgb(127, 187, 179)';")
    media = js(message + "const e=b.contentDocument.querySelector('#fixture-image');return {src:e.getAttribute('src'),width:e.getAttribute('width'),filter:b.contentWindow.getComputedStyle(e).filter};")
    assert media['src'].startswith('data:image/gif;base64,') and media['width'] == '1' and media['filter'] == 'none', media
    checks += ["HTML message computed palette", "HTML inline styles unchanged", "HTML nested links", "HTML images untouched"]
    js(message + "a.document.getElementById('disableDarkReader').click();return true;")
    wait(message + "const e=b?.contentDocument?.querySelector('#authored');return e && b.contentWindow.getComputedStyle(e).backgroundColor==='rgb(45, 53, 59)' && b.contentWindow.getComputedStyle(e).color==='rgb(211, 198, 170)';")
    js(message + "a.document.getElementById('disableDarkReader').click();return true;")
    wait(message + "const e=b?.contentDocument?.querySelector('#authored');return e?.style.backgroundColor==='rgb(240, 240, 240)' && b.contentWindow.getComputedStyle(e).backgroundColor==='rgb(45, 53, 59)';")
    checks += ["HTML palette with Thunderbird dark conversion enabled and disabled"]
    js(r"""
      const {MailServices}=ChromeUtils.importESModule('resource:///modules/MailServices.sys.mjs');
      const account=MailServices.accounts.accounts[0];let identity=account.defaultIdentity;
      if(!identity){identity=MailServices.accounts.createIdentity();identity.email='test@example.invalid';account.addIdentity(identity);account.defaultIdentity=identity;}
      const params=Cc['@mozilla.org/messengercompose/composeparams;1'].createInstance(Ci.nsIMsgComposeParams);
      params.type=Ci.nsIMsgCompType.New;params.format=Ci.nsIMsgCompFormat.PlainText;
      params.identity=identity;params.composeFields=Cc['@mozilla.org/messengercompose/composefields;1'].createInstance(Ci.nsIMsgCompFields);
      MailServices.compose.OpenComposeWindowWithParams(null,params);return true;
    """)
    compose = "const w=Services.wm.getMostRecentWindow('msgcompose');const e=w?.GetCurrentEditorElement?.();"
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
    wait(message + "const e=b?.contentDocument?.querySelector('#authored');return e && b.contentWindow.getComputedStyle(e).backgroundColor==='rgb(240, 240, 240)';")
    checks += ["uninstall restores authored HTML appearance"]
    print(json.dumps({"thunderbird": version, "checks": checks}, indent=2))
finally:
    client.delete_session()

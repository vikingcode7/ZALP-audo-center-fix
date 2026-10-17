# -*- coding: utf-8 -*-
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
import json, socket, threading, webbrowser, os, sqlite3, hashlib, secrets, hmac, time, re, urllib.parse, urllib.request, html as html_lib
from html.parser import HTMLParser
HOST, PORT = "0.0.0.0", int(os.environ.get("PORT", "8080"))
DATA = Path(os.environ.get("ZALP_DATA_FILE", str(Path(__file__).resolve().parent / "zalp_web_data" / "database.json")))
DEFAULT = {"projects":[{"id":"p1","name":"ZALP HOME EDITION","edition":"V1.0","status":"Működő prototípus","amplifier":"ZK-TB21","power":"18 V akkumulátor","cooling":"PS4 ventilátor","notes":""}],"speakers":[],"active":"p1"}
HTML = """<!doctype html><html lang="hu"><head><meta charset="utf-8"><meta name="google-site-verification" content="eDFg_Ej_bkm7oOh0QrNysZySk_9_09YElkRxmfmY_wE" /><meta name="viewport" content="width=device-width,initial-scale=1"><title>ZALP Web Command Center v2</title>
<style>
:root{--g:#52f59b;--bg:#07110d;--p:#10251b;--m:#9cb8a7;--b:#234b36}*{box-sizing:border-box}body{margin:0;background:radial-gradient(ellipse at top,#123322,#07110d 65%);color:#eafff1;font:15px/1.5 Segoe UI,Arial}header{padding:20px 16px 14px;border-bottom:1px solid var(--b);background:#07110dee;position:sticky;top:0}.wrap,main{max-width:1150px;margin:auto}.brand{display:flex;gap:12px;align-items:center}.logo{border:1px solid var(--g);border-radius:13px;width:48px;height:48px;display:grid;place-items:center;color:var(--g);font-size:22px;font-weight:900}h1{font-size:clamp(19px,3vw,28px);margin:0}.muted,.sub{color:var(--m);font-size:13px}nav{display:flex;gap:7px;flex-wrap:wrap;margin-top:16px}.tab{background:#0b1a12;border:1px solid var(--b);color:var(--m);padding:10px 13px;border-radius:10px;cursor:pointer;font-weight:700}.tab.active,.tab:hover{background:var(--g);color:#06150d}main{padding:22px 16px 40px}.page{display:none}.page.active{display:block}.grid{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:14px}.card{background:linear-gradient(145deg,#10251b,#0a1710);border:1px solid var(--b);border-radius:15px;padding:18px;min-width:0}.card h2{font-size:18px;color:var(--g);margin:0 0 12px}.stats{display:grid;grid-template-columns:repeat(3,1fr);gap:10px}.stat,.item,.result{background:#07130c;border:1px solid var(--b);padding:12px;border-radius:10px;margin-top:10px}.stat b,.item strong{display:block;color:var(--g);font-size:17px}.stat span{font-size:12px;color:var(--m)}label{display:block;color:var(--m);font-size:13px;margin:10px 0 4px}input,textarea{width:100%;padding:10px;border:1px solid #315b42;border-radius:8px;background:#06110b;color:#eafff1;font:inherit}textarea{min-height:70px}button.primary{margin-top:12px;border:0;background:var(--g);color:#06150d;padding:10px 14px;border-radius:8px;font-weight:800;cursor:pointer}button.secondary,button.danger{margin-top:8px;border:1px solid var(--b);background:var(--p);color:#eafff1;padding:8px 11px;border-radius:8px;cursor:pointer}.danger{color:#ffbaba!important}.result{color:var(--g);white-space:pre-wrap}.notice{padding:12px;border:1px solid #705b23;background:#2a230d;color:#ffd36a;border-radius:10px;margin-top:14px;font-size:13px}.empty{color:var(--m);border:1px dashed var(--b);padding:14px;border-radius:9px}.actions{display:flex;gap:6px;flex-wrap:wrap}footer{text-align:center;padding:18px;color:var(--m);font-size:12px;border-top:1px solid var(--b)}@media(max-width:700px){header{position:static}.grid{grid-template-columns:1fr}.stats{grid-template-columns:1fr}.tab{flex:1 1 40%;padding:10px 6px}main{padding:15px 10px 30px}.card{padding:14px}}

.auth-shade{position:fixed;inset:0;background:#020805ed;z-index:1000;display:none;align-items:center;justify-content:center;padding:18px}
.auth-box{width:min(440px,100%);background:#10251b;border:1px solid var(--g);border-radius:18px;padding:22px;box-shadow:0 20px 70px #000a}
.auth-box h2{color:var(--g);margin:0 0 8px}.auth-box p{color:var(--m);font-size:13px}.auth-switch{display:flex;gap:8px;margin:12px 0}.auth-switch button{flex:1}
#cookieBanner{position:fixed;bottom:12px;left:12px;right:12px;z-index:1100;max-width:850px;margin:auto;background:#10251b;border:1px solid var(--g);border-radius:14px;padding:16px;box-shadow:0 10px 40px #0009;display:none}
.cookie-actions{display:flex;gap:8px;flex-wrap:wrap;margin-top:10px}.accountbar{display:flex;align-items:center;gap:10px;justify-content:flex-end;margin-top:10px;color:var(--m);font-size:13px}
@media(max-width:700px){.auth-box{padding:16px}.accountbar{justify-content:flex-start;flex-wrap:wrap}}
</style></head><body><div class="auth-shade" id="authShade"><div class="auth-box">
<h2>🔐 ZALP-fiók</h2><p>Minden fiók saját, elkülönített projekt- és hangszóró-adatokat kap.</p>
<div class="auth-switch"><button class="secondary" type="button" onclick="authMode('login')">Bejelentkezés</button><button class="secondary" type="button" onclick="authMode('register')">Fiók létrehozása</button></div>
<form id="authForm"><label>Felhasználónév</label><input id="authUser" autocomplete="username" minlength="3" maxlength="32" required pattern="[A-Za-z0-9_.-]+" placeholder="pl. zalp_user">
<label>Jelszó</label><input id="authPass" type="password" autocomplete="current-password" minlength="10" required placeholder="Legalább 10 karakter">
<button class="primary" id="authSubmit" type="submit">Bejelentkezés</button><div class="result" id="authMessage" aria-live="polite"></div></form>
<p>Ne használj máshol is használt jelszót. A jelszavadat nem tároljuk olvasható formában.</p>
</div></div><header><div class="wrap"><div class="brand"><div class="logo">Z</div><div><h1>ZALP WEB COMMAND CENTER v2.0</h1><div class="sub">AUDIO SYSTEMS • LOCAL DASHBOARD</div></div></div><div class="accountbar"><span id="accountLabel">Nincs bejelentkezve</span><button class="secondary" id="logoutBtn" style="display:none" onclick="logout()">Kijelentkezés</button></div><nav><button class="tab active" data-page="home">Áttekintés</button><button class="tab" data-page="audio">Audio Designer</button><button class="tab" data-page="power">Power Station</button><button class="tab" data-page="speakers">Hangszórók</button><button class="tab" data-page="projects">Projektek</button><button class="tab" data-page="advisor">🤖 AI Audio Advisor</button></nav></div></header><main>
<section class="page active" id="home"><div class="card"><b style="color:var(--g)">● RENDSZER ONLINE</b><h2>ZALP vezérlőközpont</h2><p class="muted">Projekt- és hangszóró-adatbázis, mobilbarát felület.</p><div class="stats"><div class="stat"><b>v2.0</b><span>Webes dashboard</span></div><div class="stat"><b id="pc">1</b><span>Projekt</span></div><div class="stat"><b id="sc">0</b><span>Hangszóró</span></div></div></div><div class="grid"><div class="card"><h2>Gyorsindítás</h2><p>🔊 Doboz és reflexcső kalkulátor</p><p>⚡ Teljesítmény és üzemidő</p><p>📚 Hangszórók mentése</p><p>🗂️ Több projekt kezelése</p></div><div class="card"><h2>Aktív projekt</h2><div id="summary" class="muted">Betöltés…</div><button class="secondary" onclick="tab('projects')">Projektek kezelése</button></div></div><div class="notice">A fiókod adatai elkülönítve tárolódnak. A szolgáltatás csak a szükséges bejelentkezési munkamenet-sütit használja; analitikai és reklámsütik nincsenek bekapcsolva.</div></section>
<section class="page" id="audio"><div class="grid"><div class="card"><h2>Doboz térfogata</h2><label>Hossz (cm)</label><input id="len" type="number" value="40"><label>Szélesség (cm)</label><input id="wid" type="number" value="30"><label>Magasság (cm)</label><input id="hei" type="number" value="30"><button class="primary" onclick="volume()">Számítás</button><div class="result" id="vr">Eredmény</div></div><div class="card"><h2>Reflexcső-becslő</h2><label>Nettó térfogat (liter)</label><input id="bv" type="number" value="30"><label>Célfrekvencia (Hz)</label><input id="freq" type="number" value="40"><label>Cső belső átmérője (cm)</label><input id="dia" type="number" value="7"><button class="primary" onclick="port()">Csőhossz becslése</button><div class="result" id="pr">Eredmény</div></div></div><div class="notice">A reflexcsőhossz közelítő becslés; a tényleges hangolás a hangszórótól és dobozkialakítástól is függ.</div></section>
<section class="page" id="power"><div class="grid"><div class="card"><h2>Teljesítmény</h2><label>Feszültség (V)</label><input id="volt" type="number" value="18"><label>Áramerősség (A)</label><input id="amp" type="number" value="5"><button class="primary" onclick="power()">P = U × I</button><div class="result" id="powr">Eredmény</div></div><div class="card"><h2>Akkumulátor-üzemidő</h2><label>Feszültség (V)</label><input id="bvolt" type="number" value="18"><label>Kapacitás (Ah)</label><input id="ah" type="number" value="4"><label>Fogyasztás (W)</label><input id="load" type="number" value="30"><button class="primary" onclick="battery()">Üzemidő becslése</button><div class="result" id="br">Eredmény</div></div><div class="card"><h2>Ohm-törvény</h2><label>Mit számoljunk?</label><select id="ot"><option value="r">Ellenállás R=U/I</option><option value="i">Áram I=U/R</option><option value="u">Feszültség U=I×R</option></select><label>U (V)</label><input id="ou" type="number" value="12"><label>I (A)</label><input id="oi" type="number" value="2"><label>R (Ω)</label><input id="or" type="number" value="6"><button class="primary" onclick="ohm()">Kiszámítás</button><div class="result" id="orr">Eredmény</div></div></div></section>
<section class="page" id="speakers"><div class="grid"><div class="card"><h2>Hangszóró-adatlap</h2><label>Megnevezés</label><input id="sn" placeholder="ZALP 10 inch subwoofer"><label>Átmérő (inch)</label><input id="ss" type="number" placeholder="10"><label>Impedancia (Ω)</label><input id="si" type="number" placeholder="4"><label>Névleges teljesítmény (W)</label><input id="sw" type="number" placeholder="200"><label>Megjegyzés</label><textarea id="snote" placeholder="Típus, érzékenység, T/S adatok…"></textarea><button class="primary" onclick="addSpeaker()">Hangszóró mentése</button><div class="result" id="sres"></div></div><div class="card"><h2>Mentett hangszórók</h2><div id="slist" class="empty">Betöltés…</div></div></div></section>
<section class="page" id="projects"><div class="grid"><div class="card"><h2>Új projekt</h2><label>Projekt neve</label><input id="pn" placeholder="RoadBass RS540W"><label>Verzió</label><input id="pe" placeholder="V1.0"><label>Állapot</label><input id="pst" placeholder="Tervezés alatt"><label>Erősítő</label><input id="pa" placeholder="ZK-TB21"><label>Tápellátás</label><input id="pp" placeholder="18 V akkumulátor"><label>Hűtés</label><input id="pc" placeholder="Ventilátor"><label>Megjegyzések</label><textarea id="pnote"></textarea><button class="primary" onclick="addProject()">Projekt mentése</button><div class="result" id="pres"></div></div><div class="card"><h2>Projektjeim</h2><div id="plist" class="empty">Betöltés…</div></div></div></section>
<section class="page" id="advisor"><div class="card"><h2>🤖 ZALP AI Audio Advisor</h2><p class="muted">Add meg az igényeidet, majd keress valós webes termékoldalakat. A műszaki ellenőrzés külön értékeli a megadott adatokat; a találatok adatait mindig ellenőrizd a gyártónál.</p>
<div class="grid"><div><label>Mit keressünk?</label><select id="adCategory"><option value="subwoofer">Mélyhangszóró / mélynyomó</option><option value="midrange">Középhangszóró</option><option value="tweeter">Magassugárzó</option><option value="speaker">Teljes hangszóró</option><option value="amplifier">Erősítő</option><option value="power_supply">Tápegység / tápegységmodul</option></select></div><div><label>Használat</label><select id="adUse"><option value="car audio">Autóhifi</option><option value="home audio">Otthoni hangrendszer</option><option value="DIY audio amplifier">DIY / saját építésű rendszer</option></select></div></div>
<div class="grid">
<div><h2>Hangszóró</h2><label>Hangszóró neve</label><input id="adSpeaker" placeholder="Pl. ZALP 10 inch subwoofer"><label>Teljesítmény (W RMS)</label><input id="adSpeakerW" type="number" min="1" value="200"><label>Impedancia (Ω)</label><input id="adSpeakerOhm" type="number" min="1" step="0.5" value="4"><label>Ár</label><input id="adSpeakerPrice" type="number" min="0" value="18000"></div>
<div><h2>Erősítő és táp</h2><label>Erősítő neve</label><input id="adAmp" placeholder="Pl. ZK-TB21"><label>Kimenő teljesítmény az adott Ω-on (W RMS)</label><input id="adAmpW" type="number" min="1" value="100"><label>Erősítő minimális terhelése (Ω)</label><input id="adAmpMinOhm" type="number" min="1" step="0.5" value="4"><label>Tápfeszültség (V)</label><input id="adVolt" type="number" min="1" value="18"><label>Erősítő megengedett tápfeszültsége (V)</label><div class="grid"><input id="adVmin" aria-label="Minimális tápfeszültség" type="number" min="1" value="12"><input id="adVmax" aria-label="Maximális tápfeszültség" type="number" min="1" value="24"></div><label>Erősítő ára</label><input id="adAmpPrice" type="number" min="0" value="12000"></div>
</div>
<div class="grid"><div><label>Költségkeret</label><input id="adBudget" type="number" min="0" value="35000"></div><div><label>Pénznem</label><select id="adCurrency"><option value="HUF">Forint (Ft)</option><option value="EUR">Euró (€)</option></select></div></div>
<div class="actions"><button class="primary" onclick="getAdvice()">Műszaki párosítás ellenőrzése</button><button class="primary" onclick="searchProducts()">🌐 Termékek keresése a neten</button></div><div class="result" id="adResult" aria-live="polite">Töltsd ki az igényeket, majd válassz keresést.</div><div id="adWebResults"></div>
<div class="notice">A webes keresés külső termékoldalakat gyűjt össze; nem minden oldal ad vissza árat vagy műszaki adatot. A rendszer nem talál ki hiányzó adatokat. Ez egy webes kereső + műszaki ajánló alapverzió; valódi generatív AI-modell API-ja még nincs bekötve.</div></div></section></main><footer>ZALP WEB COMMAND CENTER v2.2 • AI AUDIO ADVISOR</footer> • fiókonként elkülönített adatok</footer>
<div id="cookieBanner"><strong>🍪 Süti-beállítások</strong><p>Az oldal a bejelentkezéshez szükséges munkamenet-sütit használ. Jelenleg nem használunk analitikai vagy reklámsütiket. A választásodat ezen az eszközön mentjük el.</p><div class="cookie-actions"><button class="primary" onclick="cookieChoice('necessary')">Csak szükséges sütik</button><button class="secondary" onclick="cookieChoice('all')">Elfogadom</button></div></div>
<script>
const $=id=>document.getElementById(id), n=id=>Number($(id).value), f=x=>x.toLocaleString('hu-HU',{maximumFractionDigits:2});
function tab(id){document.querySelectorAll('.tab').forEach(b=>b.classList.toggle('active',b.dataset.page===id));document.querySelectorAll('.page').forEach(p=>p.classList.toggle('active',p.id===id));if(id==='projects'||id==='speakers')refresh();window.scrollTo({top:0,behavior:'smooth'})}document.querySelectorAll('.tab').forEach(b=>b.addEventListener('click',()=>tab(b.dataset.page)));
function volume(){let a=n('len'),b=n('wid'),c=n('hei');$('vr').textContent=a>0&&b>0&&c>0?`Bruttó térfogat: ${f(a*b*c/1000)} liter\\nA hangszóró és merevítések térfogatát vond le.`:'Adj meg pozitív méreteket.'}
function port(){let v=n('bv'),h=n('freq'),d=n('dia'),l=23562.5*d*d/(h*h*v)-.732*d;$('pr').textContent=v>0&&h>0&&d>0&&l>0?`Becsült csőhossz: ${f(l)} cm`:'Ellenőrizd az értékeket.'}
function power(){let u=n('volt'),i=n('amp');$('powr').textContent=u>0&&i>0?`Elektromos bemenő teljesítmény: ${f(u*i)} W`:'Adj meg pozitív értékeket.'}
function battery(){let u=n('bvolt'),a=n('ah'),w=n('load'),h=u*a/w;$('br').textContent=u>0&&a>0&&w>0?`Névleges energia: ${f(u*a)} Wh\\nElméleti üzemidő: ${f(h)} óra (${f(h*60)} perc)\\nA valós üzemidő rövidebb lehet.`:'Adj meg pozitív értékeket.'}
function ohm(){let t=$('ot').value,u=n('ou'),i=n('oi'),r=n('or'),v,unit;if(t==='r'){v=u/i;unit='Ω'}else if(t==='i'){v=u/r;unit='A'}else{v=i*r;unit='V'}$('orr').textContent=Number.isFinite(v)&&v>=0?`Eredmény: ${f(v)} ${unit}`:'Ellenőrizd az értékeket.'}
let authAction='login', currentUser=null;
async function api(url,opt={}){let r=await fetch(url,{credentials:'same-origin',headers:{'Content-Type':'application/json',...(opt.headers||{})},...opt}),j=await r.json().catch(()=>({error:'Szerverhiba'}));if(r.status===401&&url!=='/api/me'){showAuth();throw Error('Jelentkezz be újra.')}if(!r.ok||j.error)throw Error(j.error||'Szerverhiba');return j}
function showAuth(){ $('authShade').style.display='flex'; $('logoutBtn').style.display='none'; $('accountLabel').textContent='Bejelentkezés szükséges'; }
function hideAuth(){ $('authShade').style.display='none'; }
function authMode(mode){authAction=mode;$('authSubmit').textContent=mode==='login'?'Bejelentkezés':'Fiók létrehozása';$('authPass').autocomplete=mode==='login'?'current-password':'new-password';$('authMessage').textContent=mode==='register'?'A felhasználónév 3–32 karakter; a jelszó legalább 10 karakter legyen.':'';}
$('authForm').addEventListener('submit',async ev=>{ev.preventDefault();$('authMessage').textContent='Feldolgozás…';try{let j=await api('/api/'+(authAction==='register'?'register':'login'),{method:'POST',body:JSON.stringify({username:$('authUser').value.trim(),password:$('authPass').value})});currentUser=j.username;$('accountLabel').textContent='Bejelentkezve: '+j.username;$('logoutBtn').style.display='inline-block';hideAuth();$('authPass').value='';await refresh();}catch(e){$('authMessage').textContent=e.message;}});
async function logout(){try{await api('/api/logout',{method:'POST',body:'{}'});}catch(e){}currentUser=null;showAuth();}
function cookieChoice(choice){try{localStorage.setItem('zalp_cookie_choice',choice)}catch(e){}$('cookieBanner').style.display='none';}
function initCookies(){try{if(!localStorage.getItem('zalp_cookie_choice'))$('cookieBanner').style.display='block'}catch(e){$('cookieBanner').style.display='block'}}

function esc(s){return String(s??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]))}
async function refresh(){try{let d=await api('/api/db');$('pc').textContent=d.projects.length;$('sc').textContent=d.speakers.length;let a=d.projects.find(p=>p.id===d.active)||d.projects[0];$('summary').innerHTML=a?`<p><b>${esc(a.name)}</b> ${esc(a.edition||'')}</p><p>Erősítő: ${esc(a.amplifier||'—')}</p><p>Táp: ${esc(a.power||'—')}</p><p>Állapot: ${esc(a.status||'—')}</p>`:'Nincs projekt';$('plist').innerHTML=d.projects.length?d.projects.map(p=>`<div class="item"><strong>${esc(p.name)}</strong><p>${esc(p.edition||'')} • ${esc(p.status||'')}</p><div class="actions"><button class="secondary" onclick="activate('${esc(p.id)}')">${p.id===d.active?'Aktív':'Aktiválás'}</button><button class="danger" onclick="delProject('${esc(p.id)}')">Törlés</button></div></div>`).join(''):'<div class="empty">Nincs projekt.</div>';$('slist').innerHTML=d.speakers.length?d.speakers.map(s=>`<div class="item"><strong>${esc(s.name)}</strong><p>${esc(s.size||'')}″ • ${esc(s.impedance||'')} Ω • ${esc(s.watts||'')} W</p><p>${esc(s.notes||'')}</p><button class="danger" onclick="delSpeaker('${esc(s.id)}')">Törlés</button></div>`).join(''):'<div class="empty">Még nincs mentett hangszóró.</div>'}catch(e){console.error(e)}}
async function addProject(){let p={name:$('pn').value.trim(),edition:$('pe').value,status:$('pst').value,amplifier:$('pa').value,power:$('pp').value,cooling:$('pc').value,notes:$('pnote').value};if(!p.name)return $('pres').textContent='A projekt neve kötelező.';try{await api('/api/projects',{method:'POST',body:JSON.stringify(p)});$('pres').textContent='Projekt elmentve!';['pn','pe','pst','pa','pp','pc','pnote'].forEach(x=>$(x).value='');refresh()}catch(e){$('pres').textContent=e.message}}
async function activate(id){try{await api('/api/active',{method:'POST',body:JSON.stringify({id})});refresh()}catch(e){alert(e.message)}}
async function delProject(id){if(!confirm('Biztosan törlöd a projektet?'))return;try{await api('/api/project-delete',{method:'POST',body:JSON.stringify({id})});refresh()}catch(e){alert(e.message)}}
async function addSpeaker(){let s={name:$('sn').value.trim(),size:$('ss').value,impedance:$('si').value,watts:$('sw').value,notes:$('snote').value};if(!s.name)return $('sres').textContent='A név kötelező.';try{await api('/api/speakers',{method:'POST',body:JSON.stringify(s)});$('sres').textContent='Hangszóró elmentve!';['sn','ss','si','sw','snote'].forEach(x=>$(x).value='');refresh()}catch(e){$('sres').textContent=e.message}}
async function delSpeaker(id){if(!confirm('Biztosan törlöd a hangszórót?'))return;try{await api('/api/speaker-delete',{method:'POST',body:JSON.stringify({id})});refresh()}catch(e){alert(e.message)}}
async function getAdvice(){const ids=['adSpeaker','adSpeakerW','adSpeakerOhm','adSpeakerPrice','adAmp','adAmpW','adAmpMinOhm','adVolt','adVmin','adVmax','adAmpPrice','adBudget','adCurrency'];const d={};ids.forEach(id=>d[id]=$(id).value);$('adResult').textContent='Elemzés…';try{const r=await api('/api/advisor',{method:'POST',body:JSON.stringify(d)});$('adResult').textContent=r.summary}catch(e){$('adResult').textContent=e.message}}
async function searchProducts(){const d={category:$('adCategory').value,use:$('adUse').value,budget:$('adBudget').value,currency:$('adCurrency').value,voltage:$('adVolt').value,ohms:$('adSpeakerOhm').value,watts:$('adSpeakerW').value,ampWatts:$('adAmpW').value};$('adWebResults').innerHTML='<div class="result">Keresés a weben…</div>';$('adResult').textContent='Keresési igény összeállítása…';try{const r=await api('/api/product-search',{method:'POST',body:JSON.stringify(d)});$('adResult').textContent=r.note;$('adWebResults').innerHTML=r.results.length?r.results.map(x=>`<div class="item"><strong>${esc(x.title)}</strong><p>${esc(x.snippet||'A találatban nincs leírás.')}</p><a href="${esc(x.url)}" target="_blank" rel="noopener noreferrer">Termékoldal megnyitása ↗</a></div>`).join(''):'<div class="empty">Nem találtunk feldolgozható termékoldalt. Próbáld újra más kulcsszavakkal.</div>'}catch(e){$('adWebResults').innerHTML='';$('adResult').textContent='A webes keresés most nem sikerült: '+e.message}}
async function boot(){initCookies();try{let j=await api('/api/me');currentUser=j.username;$('accountLabel').textContent='Bejelentkezve: '+j.username;$('logoutBtn').style.display='inline-block';hideAuth();await refresh();}catch(e){showAuth();}}
boot();
</script></body></html>"""



DB_FILE = Path(os.environ.get("ZALP_DB_FILE", str(Path(os.environ.get("ZALP_DATA_DIR", "/app/zalp_web_data")) / "zalp_accounts.sqlite3")))
SESSION_SECONDS = 7 * 24 * 60 * 60
PBKDF2_ROUNDS = 310_000
USERNAME_RE = re.compile(r"^[A-Za-z0-9_.-]{3,32}$")

def connect_db():
    DB_FILE.parent.mkdir(parents=True, exist_ok=True)
    con = sqlite3.connect(str(DB_FILE), timeout=20)
    con.row_factory = sqlite3.Row
    con.execute("PRAGMA foreign_keys=ON")
    return con

def init_db():
    with connect_db() as con:
        con.execute("""CREATE TABLE IF NOT EXISTS users (
            id TEXT PRIMARY KEY, username TEXT NOT NULL UNIQUE COLLATE NOCASE,
            password_hash TEXT NOT NULL, salt TEXT NOT NULL, created_at INTEGER NOT NULL
        )""")
        con.execute("""CREATE TABLE IF NOT EXISTS sessions (
            token_hash TEXT PRIMARY KEY, user_id TEXT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
            expires_at INTEGER NOT NULL
        )""")
        con.execute("""CREATE TABLE IF NOT EXISTS user_data (
            user_id TEXT PRIMARY KEY REFERENCES users(id) ON DELETE CASCADE,
            db_json TEXT NOT NULL, updated_at INTEGER NOT NULL
        )""")
        con.execute("CREATE INDEX IF NOT EXISTS sessions_expiry ON sessions(expires_at)")
        con.execute("DELETE FROM sessions WHERE expires_at < ?", (int(time.time()),))

def default_db():
    return json.loads(json.dumps(DEFAULT))

def hash_password(password, salt):
    return hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), bytes.fromhex(salt), PBKDF2_ROUNDS).hex()

def create_session(user_id):
    token = secrets.token_urlsafe(32)
    token_hash = hashlib.sha256(token.encode()).hexdigest()
    with connect_db() as con:
        con.execute("INSERT INTO sessions(token_hash,user_id,expires_at) VALUES(?,?,?)",
                    (token_hash, user_id, int(time.time()) + SESSION_SECONDS))
    return token

def get_session_user(handler):
    raw = handler.headers.get("Cookie", "")
    token = None
    for part in raw.split(";"):
        key, sep, value = part.strip().partition("=")
        if sep and key == "zalp_session":
            token = value
            break
    if not token:
        return None
    token_hash = hashlib.sha256(token.encode()).hexdigest()
    with connect_db() as con:
        row = con.execute("""SELECT users.id, users.username FROM sessions
            JOIN users ON users.id=sessions.user_id
            WHERE sessions.token_hash=? AND sessions.expires_at>?""",
            (token_hash, int(time.time()))).fetchone()
    return dict(row) if row else None

def load_user_db(user_id):
    with connect_db() as con:
        row = con.execute("SELECT db_json FROM user_data WHERE user_id=?", (user_id,)).fetchone()
        if row:
            try:
                data = json.loads(row["db_json"])
                if isinstance(data, dict) and isinstance(data.get("projects"), list) and isinstance(data.get("speakers"), list):
                    return data
            except Exception:
                pass
        data = default_db()
        con.execute("INSERT OR REPLACE INTO user_data(user_id,db_json,updated_at) VALUES(?,?,?)",
                    (user_id, json.dumps(data, ensure_ascii=False), int(time.time())))
        return data

def save_user_db(user_id, data):
    with connect_db() as con:
        con.execute("INSERT INTO user_data(user_id,db_json,updated_at) VALUES(?,?,?) "
                    "ON CONFLICT(user_id) DO UPDATE SET db_json=excluded.db_json,updated_at=excluded.updated_at",
                    (user_id, json.dumps(data, ensure_ascii=False), int(time.time())))

def send_json(h, data, status=200, extra_headers=None):
    raw=json.dumps(data,ensure_ascii=False).encode()
    h.send_response(status)
    h.send_header("Content-Type","application/json; charset=utf-8")
    h.send_header("Content-Length",str(len(raw)))
    h.send_header("Cache-Control","no-store")
    for key, value in (extra_headers or []):
        h.send_header(key, value)
    h.end_headers()
    h.wfile.write(raw)

def set_session_cookie(handler, token):
    secure = handler.headers.get("X-Forwarded-Proto", "").lower() == "https" or handler.headers.get("Host", "").endswith(".up.railway.app")
    cookie = f"zalp_session={token}; Path=/; HttpOnly; SameSite=Lax; Max-Age={SESSION_SECONDS}"
    if secure: cookie += "; Secure"
    return [("Set-Cookie", cookie)]

def clear_session_cookie(handler):
    secure = handler.headers.get("X-Forwarded-Proto", "").lower() == "https" or handler.headers.get("Host", "").endswith(".up.railway.app")
    cookie = "zalp_session=; Path=/; HttpOnly; SameSite=Lax; Max-Age=0"
    if secure: cookie += "; Secure"
    return [("Set-Cookie", cookie)]

def origin_ok(handler):
    origin = handler.headers.get("Origin")
    if not origin: return True
    from urllib.parse import urlparse
    try: return urlparse(origin).netloc.lower() == handler.headers.get("Host", "").lower()
    except Exception: return False

class SearchResultsParser(HTMLParser):
    """Small, dependency-free parser for DuckDuckGo HTML search results."""
    def __init__(self):
        super().__init__(); self.results=[]; self.current=None; self.capture=None
    def handle_starttag(self, tag, attrs):
        a=dict(attrs)
        classes=a.get("class", "")
        if tag == "a" and "result__a" in classes.split():
            self.current={"url":a.get("href", ""), "title":"", "snippet":""}; self.capture="title"
        elif self.current is not None and tag in ("a", "div") and "result__snippet" in classes.split():
            self.capture="snippet"
    def handle_data(self, data):
        if self.current is not None and self.capture in ("title", "snippet"):
            self.current[self.capture] += data
    def handle_endtag(self, tag):
        if self.current is not None and tag == "a" and self.capture == "title":
            if self.current.get("url", "").startswith("http") and self.current.get("title", "").strip():
                self.results.append({k:html_lib.unescape(v).strip() for k,v in self.current.items()})
            self.current=None; self.capture=None
        elif self.current is not None and tag == "div" and self.capture == "snippet":
            self.capture=None

def search_web_products(data):
    categories={"subwoofer":"subwoofer mélynyomó hangszóró", "midrange":"közép hangszóró midrange driver", "tweeter":"magassugárzó tweeter", "speaker":"hangszóró driver", "amplifier":"audio erősítő amplifier", "power_supply":"tápegység kapcsolóüzemű tápegység"}
    category=str(data.get("category", "subwoofer")); category=category if category in categories else "subwoofer"
    use=str(data.get("use", "DIY audio"))[:40]
    currency=str(data.get("currency", "HUF")); currency=currency if currency in ("HUF", "EUR") else "HUF"
    try: budget=max(0,float(data.get("budget",0)))
    except (TypeError,ValueError): budget=0
    try: voltage=max(0,float(data.get("voltage",0)))
    except (TypeError,ValueError): voltage=0
    try: ohms=max(0,float(data.get("ohms",0)))
    except (TypeError,ValueError): ohms=0
    try: watts=max(0,float(data.get("watts",0)))
    except (TypeError,ValueError): watts=0
    try: amp_watts=max(0,float(data.get("ampWatts",0)))
    except (TypeError,ValueError): amp_watts=0
    terms=[categories[category], use]
    if category in ("amplifier", "power_supply") and voltage: terms.append(f"{voltage:g}V")
    if category in ("subwoofer","midrange","tweeter","speaker") and ohms: terms.append(f"{ohms:g} ohm")
    if category in ("subwoofer","midrange","tweeter","speaker") and watts: terms.append(f"{watts:g}W RMS")
    if category=="amplifier" and amp_watts: terms.append(f"{amp_watts:g}W RMS")
    terms.append("ár" if currency=="HUF" else "price EUR")
    if budget: terms.append(f"under {budget:g} {currency}")
    query=" ".join(terms)
    url="https://html.duckduckgo.com/html/?"+urllib.parse.urlencode({"q":query,"kl":"hu-hu"})
    req=urllib.request.Request(url,headers={"User-Agent":"Mozilla/5.0 (compatible; ZALPAudioAdvisor/1.0)","Accept-Language":"hu-HU,hu;q=0.9,en;q=0.7"})
    with urllib.request.urlopen(req,timeout=12) as response:
        page=response.read(1_500_000).decode("utf-8","replace")
    parser=SearchResultsParser(); parser.feed(page)
    seen=set(); results=[]
    for item in parser.results:
        target=item["url"]
        if target in seen: continue
        seen.add(target)
        results.append({"title":item["title"][:220],"url":target,"snippet":item.get("snippet","")[:500]})
        if len(results)>=8: break
    return query, results

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/":
            raw=HTML.encode()
            self.send_response(200)
            self.send_header("Content-Type","text/html; charset=utf-8")
            self.send_header("Content-Length",str(len(raw)))
            self.send_header("Cache-Control","no-store")
            self.end_headers()
            self.wfile.write(raw)
        elif self.path == "/api/me":
            user = get_session_user(self)
            if not user: return send_json(self, {"error":"Nincs aktív bejelentkezés."}, 401)
            send_json(self, {"ok":True, "username":user["username"]})
        elif self.path == "/api/db":
            user = get_session_user(self)
            if not user: return send_json(self, {"error":"Bejelentkezés szükséges."}, 401)
            send_json(self, load_user_db(user["id"]))
        else: self.send_error(404)

    def do_POST(self):
        if not origin_ok(self): return send_json(self, {"error":"A kérés eredete nem engedélyezett."}, 403)
        try:
            length=int(self.headers.get("Content-Length","0"))
            if length > 100000: raise ValueError("Túl nagy kérés")
            data=json.loads(self.rfile.read(length).decode() or "{}")
            path=self.path
            if path == "/api/register":
                username=str(data.get("username","")).strip()
                password=str(data.get("password",""))
                if not USERNAME_RE.fullmatch(username):
                    return send_json(self, {"error":"A felhasználónév 3–32 karakter legyen; csak angol betű, szám, pont, kötőjel és aláhúzás használható."}, 400)
                if len(password) < 10 or len(password) > 256:
                    return send_json(self, {"error":"A jelszó legalább 10, legfeljebb 256 karakter legyen."}, 400)
                user_id="u"+secrets.token_hex(16)
                salt=secrets.token_bytes(16).hex()
                pw_hash=hash_password(password,salt)
                try:
                    with connect_db() as con:
                        con.execute("INSERT INTO users(id,username,password_hash,salt,created_at) VALUES(?,?,?,?,?)",
                                    (user_id,username,pw_hash,salt,int(time.time())))
                        con.execute("INSERT INTO user_data(user_id,db_json,updated_at) VALUES(?,?,?)",
                                    (user_id,json.dumps(default_db(),ensure_ascii=False),int(time.time())))
                except sqlite3.IntegrityError:
                    return send_json(self, {"error":"Ez a felhasználónév már foglalt."}, 409)
                token=create_session(user_id)
                return send_json(self, {"ok":True,"username":username}, 201, set_session_cookie(self,token))
            if path == "/api/login":
                username=str(data.get("username","")).strip()
                password=str(data.get("password",""))
                with connect_db() as con:
                    row=con.execute("SELECT id,username,password_hash,salt FROM users WHERE username=? COLLATE NOCASE",(username,)).fetchone()
                if not row or not hmac.compare_digest(hash_password(password,row["salt"]),row["password_hash"]):
                    return send_json(self, {"error":"Hibás felhasználónév vagy jelszó."}, 401)
                token=create_session(row["id"])
                return send_json(self, {"ok":True,"username":row["username"]}, 200, set_session_cookie(self,token))
            if path == "/api/logout":
                raw=self.headers.get("Cookie","")
                token=next((p.strip().partition("=")[2] for p in raw.split(";") if p.strip().startswith("zalp_session=")),None)
                if token:
                    with connect_db() as con:
                        con.execute("DELETE FROM sessions WHERE token_hash=?",(hashlib.sha256(token.encode()).hexdigest(),))
                return send_json(self, {"ok":True}, 200, clear_session_cookie(self))
            user = get_session_user(self)
            if not user: return send_json(self, {"error":"Bejelentkezés szükséges."}, 401)
            db=load_user_db(user["id"])
            if path=="/api/product-search":
                try:
                    query, results = search_web_products(data)
                except Exception as exc:
                    print("[ZALP SEARCH]", type(exc).__name__, str(exc)[:250])
                    return send_json(self,{"error":"A külső webes kereső nem érhető el most. Próbáld újra később."},502)
                note="Keresés: "+query+"\n\nA találatok külső webes keresésből származnak. Az ár, készlet, RMS-teljesítmény, impedancia és feszültségtartomány a termékoldalon ellenőrizendő; a keresőtalálat önmagában nem igazolja a kompatibilitást."
                return send_json(self,{"ok":True,"query":query,"note":note,"results":results})
            if path=="/api/advisor":
                def num(key):
                    try: return float(data.get(key, 0))
                    except (TypeError, ValueError): return 0.0
                sw=num("adSpeakerW"); so=num("adSpeakerOhm"); sp=num("adSpeakerPrice")
                aw=num("adAmpW"); amin=num("adAmpMinOhm"); volt=num("adVolt")
                vmin=num("adVmin"); vmax=num("adVmax"); ap=num("adAmpPrice"); budget=num("adBudget")
                currency=str(data.get("adCurrency","HUF"))
                if currency not in ("HUF","EUR"): currency="HUF"
                if min(sw,so,sp,aw,amin,volt,vmin,vmax,ap,budget) < 0 or min(sw,so,aw,amin,volt,vmin,vmax) <= 0:
                    return send_json(self,{"error":"Ellenőrizd a számokat: a teljesítmény, impedancia és feszültség legyen pozitív."},400)
                speaker=str(data.get("adSpeaker","Hangszóró")).strip()[:120] or "Hangszóró"
                amp=str(data.get("adAmp","Erősítő")).strip()[:120] or "Erősítő"
                issues=[]; good=[]
                if so < amin:
                    issues.append(f"VESZÉLY: a hangszóró {so:g} Ω-os terhelése kisebb, mint az erősítő {amin:g} Ω minimális terhelése. Így ne kösd össze.")
                else: good.append(f"Impedancia: {so:g} Ω megfelel az erősítő legalább {amin:g} Ω-os terhelési határának.")
                if not (vmin <= volt <= vmax):
                    issues.append(f"Feszültség: a megadott {volt:g} V kívül esik az erősítő {vmin:g}–{vmax:g} V tartományán.")
                else: good.append(f"Tápfeszültség: {volt:g} V a megadott {vmin:g}–{vmax:g} V tartományon belül van.")
                ratio=aw/sw
                if aw > sw:
                    issues.append(f"Az erősítő megadott {aw:g} W RMS teljesítménye nagyobb a hangszóró {sw:g} W RMS terhelhetőségénél; óvatos beállítás és limiter ajánlott.")
                elif ratio >= 0.5:
                    good.append(f"Teljesítmény: {aw:g} W RMS erősítőteljesítmény a {sw:g} W RMS hangszóró-terhelhetőség {ratio*100:.0f}%-a.")
                else:
                    issues.append(f"Az erősítő a hangszóró névleges teljesítményének csak {ratio*100:.0f}%-át adja le a megadott adatok szerint; a kívánt hangerőhöz kevés lehet.")
                total=sp+ap
                if total > budget: issues.append(f"Költségkeret: az összesen {total:,.2f} {currency} ár túllépi a {budget:,.2f} {currency} keretet.".replace(",", " "))
                else: good.append(f"Ár: összesen {total:,.2f} {currency}, a keretből {budget-total:,.2f} {currency} marad.".replace(",", " "))
                score=100
                if so < amin: score-=60
                if not (vmin <= volt <= vmax): score-=35
                if aw > sw: score-=20
                elif ratio < .5: score-=15
                if total > budget: score-=15
                score=max(0,min(100,score))
                lines=[f"ZALP AI AUDIO ADVISOR — {speaker} + {amp}",f"Kompatibilitási pontszám: {score}/100",f"Ár/teljesítmény (hangszóró): {sp/sw:.2f} {currency}/W RMS",f"Ár/teljesítmény (erősítő): {ap/aw:.2f} {currency}/W RMS",""]
                if good: lines.append("MEGFELELŐ:")
                lines.extend("✓ "+x for x in good)
                if issues: lines.extend(["","FIGYELMEZTETÉSEK:"]+["⚠ "+x for x in issues])
                lines.extend(["","ÖSSZEGZÉS: "+("A párosítás a megadott adatok alapján elfogadhatónak tűnik, de ellenőrizd a gyártói adatlapokat." if score>=80 and not any("VESZÉLY" in x or "kívül esik" in x for x in issues) else "Ezt a párosítást ne tekintsd automatikusan biztonságosnak; ellenőrizd az erősítő adatlapját, a bekötést és a valós RMS-adatokat.")])
                return send_json(self,{"ok":True,"score":score,"summary":"\\n".join(lines)})
            if path=="/api/projects":
                name=str(data.get("name","")).strip()[:120]
                if not name: return send_json(self,{"error":"A projekt neve kötelező."},400)
                p={"id":"p"+secrets.token_hex(7),"name":name,"edition":str(data.get("edition",""))[:80],"status":str(data.get("status",""))[:120],"amplifier":str(data.get("amplifier",""))[:120],"power":str(data.get("power",""))[:120],"cooling":str(data.get("cooling",""))[:120],"notes":str(data.get("notes",""))[:2000]}
                db["projects"].append(p); db["active"]=p["id"]
            elif path=="/api/active":
                pid=str(data.get("id",""))
                if not any(p["id"]==pid for p in db["projects"]): return send_json(self,{"error":"Projekt nem található"},404)
                db["active"]=pid
            elif path=="/api/project-delete":
                pid=str(data.get("id","")); db["projects"]=[p for p in db["projects"] if p["id"]!=pid]
                if not db["projects"]: db["active"]=""
                elif db["active"]==pid: db["active"]=db["projects"][0]["id"]
            elif path=="/api/speakers":
                name=str(data.get("name","")).strip()[:120]
                if not name: return send_json(self,{"error":"A hangszóró neve kötelező."},400)
                db["speakers"].append({"id":"s"+secrets.token_hex(7),"name":name,"size":str(data.get("size",""))[:30],"impedance":str(data.get("impedance",""))[:30],"watts":str(data.get("watts",""))[:30],"notes":str(data.get("notes",""))[:2000]})
            elif path=="/api/speaker-delete":
                sid=str(data.get("id","")); db["speakers"]=[s for s in db["speakers"] if s["id"]!=sid]
            else: return send_json(self,{"error":"Ismeretlen útvonal"},404)
            save_user_db(user["id"],db)
            send_json(self,{"ok":True})
        except Exception:
            send_json(self,{"error":"A kérés feldolgozása sikertelen."},400)
    def log_message(self,fmt,*args): print("[ZALP WEB] "+(fmt%args))

def main():
    init_db(); server=ThreadingHTTPServer((HOST,PORT),Handler)
    s=socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
    try: s.connect(("192.0.2.1",80)); ip=s.getsockname()[0]
    except OSError: ip="127.0.0.1"
    finally: s.close()
    print("ZALP WEB COMMAND CENTER v2.1 - ACCOUNTS")
    print(f"Ezen a gépen: http://127.0.0.1:{PORT}")
    print(f"Helyi hálózaton: http://{ip}:{PORT}")
    print(f"Fiókadatbázis: {DB_FILE}")
    if not os.environ.get("RAILWAY_ENVIRONMENT"):
        threading.Timer(.7, lambda: webbrowser.open(f"http://127.0.0.1:{PORT}")).start()
    try: server.serve_forever()
    except KeyboardInterrupt: print("ZALP szerver leáll.")
    finally: server.server_close()

if __name__=="__main__":
    try: main()
    except OSError as e: print("Indítási hiba:",e); input("Enter a kilépéshez...")

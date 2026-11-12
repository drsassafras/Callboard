(function(){let INFO={"classic":{"spots":0,"vines":false,"film":false,"grapes":false},"dionysus":{"spots":5,"vines":true,"film":true,"grapes":true}},SEL={"theme":"dionysus","mode":"light"};
const d=document.documentElement,mq=window.matchMedia?window.matchMedia("(prefers-color-scheme: dark)"):null;
const ME=document.currentScript,NONCE=ME&&ME.nonce||"",ASSETS={"decor.js":["spots","vines","film","grapes"]},GOT={};
function need(x){Object.keys(ASSETS).forEach(function(f){if(GOT[f]||!ASSETS[f].some(function(k){return x[k];}))return;GOT[f]=true;
const s=document.createElement("script");s.src="/static/"+f+"?v=__BUILD__";if(NONCE)s.nonce=NONCE;(document.head||d).appendChild(s);});}
function own(){try{const o=JSON.parse(localStorage.getItem("pc-theme")||"null");return o&&typeof o==="object"?o:null;}catch{return null;}}
function apply(){const o=own()||{};let id=INFO[o.theme]?o.theme:SEL.theme,m=o.mode||SEL.mode;if(!INFO[id])id="dionysus";
if(m==="auto")m=mq&&mq.matches?"dark":"light";if(m!=="dark")m="light";const x=INFO[id];
d.setAttribute("data-theme",id);d.setAttribute("data-mode",m);d.setAttribute("data-vines",x.vines?"on":"off");d.setAttribute("data-film",x.film?"on":"off");d.setAttribute("data-spots",x.spots?"on":"off");d.setAttribute("data-grapes",x.grapes?"on":"off");
need(x);if(window.PCDECOR)window.PCDECOR.themed();}
apply();if(mq){if(mq.addEventListener)mq.addEventListener("change",apply);else if(mq.addListener)mq.addListener(apply);}
window.PCTHEME={apply:apply,use:function(sel,info){if(info)INFO=info;SEL=sel;apply();},own:own,
setOwn:function(o){try{if(o)localStorage.setItem("pc-theme",JSON.stringify(o));else localStorage.removeItem("pc-theme");}catch{/* storage unavailable */}apply();}};})();

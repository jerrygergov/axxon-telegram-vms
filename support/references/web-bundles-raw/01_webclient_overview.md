# 01 Webclient Overview

## Bootstrap

```html
<!doctype html>
<html>
	<head>
		<meta http-equiv="X-UA-Compatible" content="IE=edge" />
		<meta charset="utf-8" />
		<link rel="shortcut icon" href="./favicon.ico" />
		<link rel="manifest" href="manifest/manifest.json" />
		<title>AxxonOne Web</title>
		<script type="module" crossorigin src="./app.js"></script>
		<link rel="modulepreload" crossorigin href="./0.js">
		<link rel="modulepreload" crossorigin href="./conn.js">
		<link rel="modulepreload" crossorigin href="./02.js">
		<link rel="modulepreload" crossorigin href="./04.js">
		<link rel="modulepreload" crossorigin href="./05.js">
		<link rel="modulepreload" crossorigin href="./03.js">
		<link rel="stylesheet" crossorigin href="./Provider.css">
		<link rel="stylesheet" crossorigin href="./main.css">
	</head>
	<body>
		<div id="splash" class="splash"></div>
		<div id="app"></div>
		<script>
			window.login = '';
			window.pass = '';
			window.layout = -1;
		</script>
	</body>
</html>

```

## app.js head

```js
import"./0.js";import{t as j,a as f,b as S,s as i,c as M,d as x,e as A,f as b,g as R,A as m,h as _,p as a,i as P,j as C,k as p,l as r,m as $,n as H,L as D,r as O,o,q as L,u as W,v as q,P as T,w as U,T as z,x as B,y as F,z as d,B as N,C as E,D as G,E as J,F as V,G as K,H as Q,I,J as X,K as y,M as Y,N as Z,O as u}from"./02.js";import{d as ee,L as v,s as se}from"./conn.js";import{q as te,M as ie,A as ae}from"./03.js";import"./04.js";import"./05.js";function*ne(){const e=yield i(M),s=yield i(x),t=yield i(A),n=yield i(b),c=R(n?.body.cells)===1;switch(s){case m.ARCH:case m.ARCH_SEARCH:{if(!e)return;_(e,t)===!1&&c&&(yield a(P.setAppMode(m.LIVE)));break}}}function*oe(){yield j([f.cameraPermissionsUpdate,S.setCamActive],ne)}function*re({payload:e}){const s=Object.keys(e);s.length!==0&&(yield a(f.checkCamsPermissions(s)))}function*ce({payload:e}){if(!e)return;const s=yield i(A),{objects:{camera_access:t}}=s;t[e.origin]===void 0&&(yield a(f.checkCamsPermissions([e.origin])))}function*de(){yield C(p.updateCams,re),yield C(S.setCamActive,ce)}function*le(){const e=yield i(b);if(!e)return;const{objects:{camera_access:s}}=yield i(A),t=Object.values(e.body.cells).map(c=>c.camera_ap).filter(c=>$(c)),n=H(t,Object.keys(s));n.length!==0&&(yield a(f.checkCamsPermissions(n)))}function*ue(){yield C([r.selectLayout,r.modifyLayout,r.submit],le)}const me=({children:e})=>{const{tokenData:s}=D(),t=O.useMemo(()=>!s||typeof s=="string"?"":"token_value"in s?s.token_value:"token"in s?s.token:s,[s]);return o.jsx(te,{token:t,children:e})};function ye(){const e=document.getElementById("splash");if(!e)return;const s=L.subscribe(()=>{W(L.getState())&&e.classList.add("splash--mini")});e.ontransitionend=()=>{e.classList.toggle("hidden",!0),s()}}function fe(){const e=document.getElementById("app");if(!e)return;q.createRoot(e).render(o.jsx(T,{store:L,children:o.jsx(U,{children:o.jsx(z,{theme:B,children:o.jsx(F,{children:o.jsx(me,{children:o.jsx(ie,{children:o.jsx(ae,{})})})})})})}))}function*pe(){const e=yield i(V),{cams:s,mode:t,time:n}=yield i(G);(yield i(J))&&(yield d(r.pending));const g=yield i(K);if(t!==m.LIVE&&(yield a(P.setAppMode(t)),n!==null)){const l=ee(n);yield a(N.setPlayback({beginTime:l,speed:0}))}if(s.length>0)return;if(e.length>0||g){const l=e[0].body.id;yield a(r.selectLayout(g||l));return}if(yield a(p.requestList()),yield d(p.doneList),yield i(Q))return;const h=yield i(I);if(h.length===0)return;const k=h.filter(l=>l.isActivated),w=k.length>0?k[0]:h[0];yield a(E.selectCam(w))}const ge="CLASSIFIER";function*he(e){yield d(p.doneList);const t=(yield i(I)).find(({displayName:n})=>n===e);t&&(yield a(E.selectCam(t)),yield a(P.setAppMode(m.ARCH_SEARCH)),yield y(Y))}function*ve(){const e=X(s=>(window.addEventListener("message",s),()=>{window.removeEventListener("message",s)}));for(;;){const{data:{type:s,camName:t}}=yield d(e);if(s===ge){yield y(he,t);return}}}function*Ce(){v.common("version %c%s","color: blue","ASIP-ANWC3-WC-120"),window.app={debug:se},yield y(ye),navigator.serviceWorker&&window.addEventListener("load",()=>{navigator.serviceWorker.register("./service-worker.js").then(e=>{v.common("Service worker for PWA registered",e)}).catch(e=>{v.common("Service worker for PWA registration failed",e)})}),yield y(fe),yield u(ve),yield d(f.userGlobalPermissionsSuccess),yield a(r.layoutListRequest()),yield d(r.layoutListSuccess),yield y(pe)}function*Le(){yield u(oe),yield u(de),yield u(ue),yield u(Ce)}Z.run(Le);
//# sourceMappingURL=app.js.map
```

"""HTML template for derived/graph/Project_Graph.html (used by build_graph.py).

One self-contained page: the D3 7.9.0 library, the graph data and the app are all inline, so the page opens with
the network off. build_graph.py fills __D3_LICENSE__, __D3__ and __DATA__. Light theme only; lane colors are a
five-slot set that passed the all-pairs colour-vision check on the light surface (blue, aqua, yellow, green,
violet; neutral grey for no lane).
"""

LICENSE = """d3 7.9.0 — https://d3js.org — Copyright 2010-2023 Mike Bostock

Permission to use, copy, modify, and/or distribute this software for any purpose
with or without fee is hereby granted, provided that the above copyright notice
and this permission notice appear in all copies.

THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHOR DISCLAIMS ALL WARRANTIES WITH
REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES OF MERCHANTABILITY AND
FITNESS. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR ANY SPECIAL, DIRECT,
INDIRECT, OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES WHATSOEVER RESULTING FROM LOSS
OF USE, DATA OR PROFITS, WHETHER IN AN ACTION OF CONTRACT, NEGLIGENCE OR OTHER
TORTIOUS ACTION, ARISING OUT OF OR IN CONNECTION WITH THE USE OR PERFORMANCE OF
THIS SOFTWARE."""

TEMPLATE = r"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Eastsound Project Graph</title>
<style>
:root {
  color-scheme: light;
  --surface: #fcfcfb; --panel: #ffffff; --ink: #0b0b0b; --ink2: #52514e; --muted: #7b7a75;
  --line: #e4e3df; --edge: #a9a8a3; --accent: #2a78d6; --chip: #f3f2ef;
}
* { box-sizing: border-box; }
html, body { margin: 0; height: 100%; background: var(--surface); color: var(--ink);
  font: 13px/1.45 system-ui, -apple-system, "Segoe UI", Roboto, Arial, sans-serif; }
#app { display: grid; grid-template-columns: 250px minmax(0, 1fr) 420px; grid-template-rows: auto minmax(0, 1fr);
  height: 100vh; }
header { grid-column: 1 / 4; display: flex; flex-wrap: wrap; align-items: center; gap: 10px 16px; padding: 8px 14px;
  border-bottom: 1px solid var(--line); background: var(--panel); }
header h1 { font-size: 15px; margin: 0; font-weight: 650; }
#status { color: var(--ink2); }
.search { position: relative; flex: 1 1 260px; max-width: 460px; }
#q { width: 100%; padding: 6px 9px; border: 1px solid #c9c8c3; border-radius: 6px; font: inherit; background: #fff; }
#results { position: absolute; top: 100%; left: 0; right: 0; z-index: 20; background: #fff; border: 1px solid #c9c8c3;
  border-radius: 6px; margin-top: 3px; max-height: 60vh; overflow: auto; display: none;
  box-shadow: 0 6px 18px rgba(0,0,0,.12); }
#results div { padding: 5px 9px; cursor: pointer; border-bottom: 1px solid var(--line); }
#results div:hover, #results div.on { background: #eef4fc; }
#results small { color: var(--muted); margin-left: 6px; }
header label { white-space: nowrap; color: var(--ink2); }
button { font: inherit; border: 1px solid #c9c8c3; background: #fff; border-radius: 6px; padding: 5px 10px; cursor: pointer; }
button:hover { background: #f3f2ef; }
aside { overflow: auto; padding: 10px 12px 20px; border-right: 1px solid var(--line); background: var(--panel); }
aside h2 { font-size: 11px; text-transform: uppercase; letter-spacing: .06em; color: var(--muted); margin: 14px 0 6px; }
aside label { display: flex; align-items: center; gap: 7px; padding: 2px 0; cursor: pointer; }
aside label .n { margin-left: auto; color: var(--muted); font-variant-numeric: tabular-nums; }
aside select { width: 100%; font: inherit; padding: 4px; }
aside .hint { color: var(--muted); font-size: 12px; margin: 4px 0 0; }
.sw { width: 12px; height: 12px; border-radius: 3px; border: 1px solid rgba(0,0,0,.35); flex: none; }
.sw.dash { border: 1.5px dashed #3d3d3a; background: #fff; }
.shape { width: 14px; height: 14px; flex: none; }
main { position: relative; overflow: hidden; }
#svg { width: 100%; height: 100%; display: block; cursor: grab; }
#svg:active { cursor: grabbing; }
#msg { position: absolute; top: 12px; left: 14px; color: var(--ink2); background: rgba(252,252,251,.9); padding: 4px 8px;
  border-radius: 6px; }
#tip { position: absolute; pointer-events: none; background: #fff; border: 1px solid #c9c8c3; border-radius: 6px;
  padding: 6px 8px; box-shadow: 0 4px 14px rgba(0,0,0,.12); display: none; max-width: 340px; z-index: 10; }
#tip b { display: block; }
#tip span { color: var(--ink2); }
line.l { stroke: var(--edge); stroke-opacity: .35; stroke-width: .6; }
line.l.hub { stroke-opacity: .07; }
line.l.hi { stroke: #3d3d3a; stroke-opacity: .85; stroke-width: 1.1; }
path.n { stroke: #3d3d3a; stroke-width: .6; cursor: pointer; }
path.n.unres { stroke-width: 1.4; stroke-dasharray: 2.2 1.6; }
path.n.sel { stroke: #0b0b0b; stroke-width: 2.4; stroke-dasharray: none; }
.dim path.n:not(.hi):not(.sel) { opacity: .16; }
.dim line.l:not(.hi) { stroke-opacity: .04; }
text.lb { font-size: 9px; fill: var(--ink); paint-order: stroke; stroke: rgba(252,252,251,.9); stroke-width: 3px;
  pointer-events: none; display: none; }
text.lb.on { display: block; }
#card { overflow: auto; padding: 12px 14px 30px; border-left: 1px solid var(--line); background: var(--panel); }
#card .empty { color: var(--muted); margin-top: 20px; }
#card h2 { font-size: 16px; margin: 0 0 6px; line-height: 1.3; }
.badges { display: flex; flex-wrap: wrap; gap: 5px; margin-bottom: 8px; }
.badge { border: 1px solid #c9c8c3; border-radius: 10px; padding: 1px 8px; font-size: 12px; color: var(--ink2);
  display: inline-flex; align-items: center; gap: 5px; }
.badge.unres { border: 1.5px dashed #3d3d3a; color: var(--ink); }
.btns { display: flex; flex-wrap: wrap; gap: 6px; margin: 8px 0 10px; }
.btns a, .btns button { text-decoration: none; color: var(--ink); border: 1px solid #c9c8c3; border-radius: 6px;
  padding: 5px 10px; background: #fff; font-size: 12.5px; }
.btns a:hover, .btns button:hover { background: #eef4fc; }
.btns .off { color: var(--muted); border-style: dashed; cursor: default; }
#card h3 { font-size: 11px; text-transform: uppercase; letter-spacing: .06em; color: var(--muted); margin: 14px 0 5px; }
#card p { margin: 0 0 6px; }
dl { display: grid; grid-template-columns: 128px 1fr; gap: 3px 10px; margin: 0; }
dt { color: var(--ink2); }
dd { margin: 0; overflow-wrap: anywhere; }
.cite { color: var(--ink2); overflow-wrap: anywhere; }
.grp { margin: 6px 0 8px; }
.grp b { font-weight: 600; }
.chip { display: inline-block; margin: 2px 3px 2px 0; padding: 1px 7px; border-radius: 9px; background: var(--chip);
  border: 1px solid #dddcd7; cursor: pointer; font-size: 12px; }
.chip:hover { background: #e3edf9; border-color: #9ec5f4; }
.chip.unres { border: 1.3px dashed #3d3d3a; }
.chip i { font-style: normal; color: var(--muted); }
.note { border: 1px solid var(--line); border-radius: 8px; padding: 8px 10px; margin-top: 8px; background: #fafaf8; }
.counts { color: var(--muted); font-size: 12px; }
@media (max-width: 1100px) {
  #app { grid-template-columns: 210px minmax(0, 1fr); grid-template-rows: auto 60vh auto; height: auto; }
  #card { grid-column: 1 / 3; border-left: 0; border-top: 1px solid var(--line); }
}
</style>
</head>
<body>
<div id="app">
  <header>
    <h1>Eastsound Project Graph</h1>
    <span id="status"></span>
    <div class="search"><input id="q" type="search" autocomplete="off" placeholder="Search a tag or name — e.g. BL-1, E7.4, blower, 26 80 00"><div id="results"></div></div>
    <label title="Hide nodes more than 2 links from the selected node"><input type="checkbox" id="focus"> Focus: 2 hops</label>
    <label title="Let focus mode pass through bid items and areas, which link hundreds of components"><input type="checkbox" id="hubs"> through bid items and areas</label>
    <button id="reset" type="button">Reset</button>
  </header>
  <aside id="filters">
    <h2>Node type (shape)</h2><div id="f-type"></div>
    <h2>Lane (color)</h2><div id="f-lane"></div>
    <h2>Area/Building</h2><select id="f-area"></select>
    <p class="hint">Picks components located in the area, plus the sheets, specs and items they link to.</p>
    <h2>Confidence</h2><div id="f-conf"></div>
    <p class="hint">Dashed outline = Unresolved. Size = number of edges.</p>
    <h2>About</h2>
    <p class="hint" id="about"></p>
  </aside>
  <main><svg id="svg" role="img" aria-label="Project graph"></svg><div id="msg">Laying out the graph…</div><div id="tip"></div></main>
  <section id="card" aria-live="polite"><div class="empty">Click a node, or search, to see its card.</div></section>
</div>
<script>
/*! __D3_LICENSE__ */
__D3__
</script>
<script type="application/json" id="graph-data">__DATA__</script>
<script>
(function () {
  "use strict";
  var DATA = JSON.parse(document.getElementById("graph-data").textContent);
  var N = DATA.nodes, E = DATA.edges;
  var LANE_COLOR = {"Civil & Site": "#2a78d6", "Process & Mechanical": "#1baf7a", "Electrical & Controls": "#eda100",
    "Structural & Building": "#008300", "Contract & General": "#4a3aa7", "No lane": "#b5b4ae"};
  var SHAPE = {"Component": d3.symbolCircle, "Sheet": d3.symbolSquare, "Spec section": d3.symbolDiamond,
    "Spec paragraph": d3.symbolTriangle, "Addendum item": d3.symbolStar, "Bid item": d3.symbolWye,
    "Area/Building": d3.symbolCross};
  var HUB = {"Bid item": 1, "Area/Building": 1};
  var HUB_EDGE = {"paid under": 1, "located in": 1};
  var CONFS = ["Verified", "Verified-Visual", "Inferred", "Unresolved"];
  var OPEN_TEXT = {"Component": "Open sheet", "Sheet": "Open sheet", "Spec section": "Open spec page",
    "Spec paragraph": "Open spec page", "Addendum item": "Open Add. 4 page", "Bid item": "Open bid form page"};

  function esc(s) { return String(s == null ? "" : s).replace(/[&<>"']/g, function (c) {
    return {"&": "&amp;", "<": "&lt;", ">": "&gt;", "\"": "&quot;", "'": "&#39;"}[c]; }); }
  function short(n) {
    if (n.type === "Area/Building") return n.label;
    if (n.type === "Addendum item") return n.id;
    return n.label.split(" · ")[0];
  }
  function radius(n) { return Math.min(26, 3.2 + Math.sqrt(n.deg) * 1.15); }
  function symbolPath(n) { return d3.symbol().type(SHAPE[n.type]).size(Math.PI * Math.pow(radius(n), 2))(); }

  N.forEach(function (n, i) { n.i = i; n.deg = 0; n.adj = []; });
  E.forEach(function (e, k) {
    N[e.s].deg++; N[e.t].deg++;
    N[e.s].adj.push({k: k, o: e.t, d: "out"}); N[e.t].adj.push({k: k, o: e.s, d: "in"});
  });
  var byId = {}; N.forEach(function (n) { byId[n.id] = n; });

  // ---------------------------------------------------------------- filters
  var state = {types: {}, lanes: {}, confs: {}, area: "", focus: false, hubs: false, sel: null};
  DATA.nodeTypes.forEach(function (t) { state.types[t] = true; });
  DATA.lanes.forEach(function (l) { state.lanes[l] = true; });
  CONFS.forEach(function (c) { state.confs[c] = true; });

  function count(pred) { var c = 0; N.forEach(function (n) { if (pred(n)) c++; }); return c; }
  function shapeIcon(t) {
    var p = d3.symbol().type(SHAPE[t]).size(60)();
    return '<svg class="shape" viewBox="-7 -7 14 14"><path d="' + p + '" fill="#d6d5d0" stroke="#3d3d3a" stroke-width=".8"/></svg>';
  }
  function box(id, key, html, n, group) {
    return '<label><input type="checkbox" checked data-g="' + group + '" data-k="' + esc(key) + '">' + html +
      '<span class="n">' + n + '</span></label>';
  }
  document.getElementById("f-type").innerHTML = DATA.nodeTypes.map(function (t) {
    return box("t", t, shapeIcon(t) + esc(t), count(function (n) { return n.type === t; }), "types"); }).join("");
  document.getElementById("f-lane").innerHTML = DATA.lanes.map(function (l) {
    return box("l", l, '<span class="sw" style="background:' + LANE_COLOR[l] + '"></span>' + esc(l),
      count(function (n) { return n.lanes.indexOf(l) >= 0; }), "lanes"); }).join("");
  document.getElementById("f-conf").innerHTML = CONFS.map(function (c) {
    return box("c", c, '<span class="sw' + (c === "Unresolved" ? " dash" : "") + '" style="background:#fff"></span>' + esc(c),
      count(function (n) { return n.conf === c; }), "confs"); }).join("");
  document.getElementById("f-area").innerHTML = '<option value="">All areas</option>' + DATA.areas.map(function (a) {
    return '<option>' + esc(a) + '</option>'; }).join("");
  document.getElementById("about").innerHTML = "Built " + esc(DATA.buildDate) + " from Project_Ledger.csv (447 rows), " +
    "index files 01–04 and the Wiki notes. The graph is a map, not a source: cite the Ledger row, Wiki note or page. " +
    "Open links are relative to this folder and open the library PDFs at the cited page.";
  document.getElementById("filters").addEventListener("change", function (ev) {
    var t = ev.target;
    if (t.dataset && t.dataset.g) { state[t.dataset.g][t.dataset.k] = t.checked; refresh(); }
    if (t.id === "f-area") { state.area = t.value; refresh(); }
  });
  document.getElementById("focus").addEventListener("change", function (ev) { state.focus = ev.target.checked; refresh(); });
  document.getElementById("hubs").addEventListener("change", function (ev) { state.hubs = ev.target.checked; refresh(); });
  document.getElementById("reset").addEventListener("click", function () {
    Array.prototype.forEach.call(document.querySelectorAll("#filters input[type=checkbox]"), function (b) {
      b.checked = true; state[b.dataset.g][b.dataset.k] = true; });
    document.getElementById("f-area").value = ""; state.area = "";
    document.getElementById("focus").checked = false; state.focus = false;
    document.getElementById("hubs").checked = false; state.hubs = false;
    select(null); fit(); refresh();
  });

  function passes(n) {
    if (!state.types[n.type] || !state.confs[n.conf]) return false;
    var lane = false;
    n.lanes.forEach(function (l) { if (state.lanes[l]) lane = true; });
    return lane;
  }
  function visibleSet() {
    var vis = new Uint8Array(N.length);
    N.forEach(function (n) { if (passes(n)) vis[n.i] = 1; });
    if (state.area) {
      var area = byId["Area " + state.area];
      var comps = new Uint8Array(N.length);
      area.adj.forEach(function (a) { if (E[a.k].type === "located in" && vis[a.o]) comps[a.o] = 1; });
      var keep = new Uint8Array(N.length);
      keep[area.i] = vis[area.i];
      N.forEach(function (n) {
        if (n.type === "Component") { keep[n.i] = comps[n.i]; return; }
        if (!vis[n.i] || n.i === area.i) return;
        n.adj.forEach(function (a) { if (comps[a.o]) keep[n.i] = 1; });
      });
      N.forEach(function (n) { if (n.type === "Spec section" && vis[n.i] && !keep[n.i]) {
        n.adj.forEach(function (a) { if (E[a.k].type === "part of" && keep[a.o]) keep[n.i] = 1; }); } });
      vis = keep;
    }
    if (state.focus && state.sel !== null && vis[state.sel]) {
      var depth = new Int8Array(N.length).fill(-1), queue = [state.sel];
      depth[state.sel] = 0;
      while (queue.length) {
        var cur = queue.shift(), cn = N[cur];
        if (depth[cur] >= 2) continue;
        if (cur !== state.sel && HUB[cn.type] && !state.hubs) continue;
        cn.adj.forEach(function (a) {
          if (vis[a.o] && depth[a.o] < 0) { depth[a.o] = depth[cur] + 1; queue.push(a.o); }
        });
      }
      for (var i = 0; i < N.length; i++) if (depth[i] < 0) vis[i] = 0;
    }
    return vis;
  }

  // ---------------------------------------------------------------- layout and drawing
  var svg = d3.select("#svg"), root = svg.append("g"), gl = root.append("g"), gn = root.append("g"), gt = root.append("g");
  var links = E.map(function (e, k) { return {source: e.s, target: e.t, k: k}; });
  var linkSel = gl.selectAll("line").data(links).join("line")
    .attr("class", function (l) { return "l" + (HUB_EDGE[E[l.k].type] ? " hub" : ""); });
  var nodeSel = gn.selectAll("path").data(N).join("path")
    .attr("class", function (n) { return "n" + (n.conf === "Unresolved" ? " unres" : ""); })
    .attr("d", symbolPath)
    .attr("fill", function (n) { return LANE_COLOR[n.lanes[0]] || LANE_COLOR["No lane"]; });
  var textSel = gt.selectAll("text").data(N).join("text").attr("class", "lb").attr("dy", "-0.7em")
    .attr("text-anchor", "middle").text(short);

  function draw() {
    linkSel.attr("x1", function (l) { return l.source.x; }).attr("y1", function (l) { return l.source.y; })
      .attr("x2", function (l) { return l.target.x; }).attr("y2", function (l) { return l.target.y; });
    nodeSel.attr("transform", function (n) { return "translate(" + n.x.toFixed(1) + "," + n.y.toFixed(1) + ")"; });
    textSel.attr("x", function (n) { return n.x; }).attr("y", function (n) { return n.y - radius(n) * 0.4; });
  }
  var zoom = d3.zoom().scaleExtent([0.05, 10]).on("zoom", function (ev) {
    root.attr("transform", ev.transform); labels(ev.transform.k); });
  svg.call(zoom).on("dblclick.zoom", null);
  var curK = 1;
  function labels(k) {
    curK = k;
    textSel.classed("on", function (n) {
      if (n._hidden) return false;
      if (state.sel !== null && (n.i === state.sel || n._near)) return true;
      if (k >= 2.2) return true;
      if (k >= 0.9) return n.deg >= 18 || n.type === "Bid item" || n.type === "Addendum item";
      return n.deg >= 60;
    });
  }
  function fit() {
    var vis = N.filter(function (n) { return !n._hidden; });
    if (!vis.length) return;
    var x0 = d3.min(vis, function (n) { return n.x; }), x1 = d3.max(vis, function (n) { return n.x; });
    var y0 = d3.min(vis, function (n) { return n.y; }), y1 = d3.max(vis, function (n) { return n.y; });
    var w = svg.node().clientWidth || 800, h = svg.node().clientHeight || 600;
    var k = Math.min(4, 0.92 / Math.max((x1 - x0 + 40) / w, (y1 - y0 + 40) / h));
    svg.transition().duration(350).call(zoom.transform,
      d3.zoomIdentity.translate(w / 2, h / 2).scale(k).translate(-(x0 + x1) / 2, -(y0 + y1) / 2));
  }

  var counts = {}; links.forEach(function (l) { counts[l.source] = (counts[l.source] || 0) + 1;
    counts[l.target] = (counts[l.target] || 0) + 1; });
  var sim = d3.forceSimulation(N)
    .force("link", d3.forceLink(links).distance(function (l) { return HUB_EDGE[E[l.k].type] ? 140 : 34; })
      .strength(function (l) {
        var s = 1 / Math.min(counts[l.source.index], counts[l.target.index]);
        return HUB_EDGE[E[l.k].type] ? s * 0.08 : s; }))
    .force("charge", d3.forceManyBody().strength(function (n) { return -26 - Math.min(n.deg, 60) * 1.6; })
      .theta(0.95).distanceMax(700))
    .force("x", d3.forceX().strength(0.035)).force("y", d3.forceY().strength(0.035))
    .force("collide", d3.forceCollide(function (n) { return radius(n) + 1.5; }))
    .stop();

  // ---------------------------------------------------------------- tooltip, hover, click, drag
  var tip = document.getElementById("tip");
  nodeSel.on("mouseenter", function (ev, n) {
    tip.innerHTML = "<b>" + esc(n.label) + "</b><span>" + esc(n.type) + " · " + esc(n.conf) + " · " + n.deg +
      " edges</span>";
    tip.style.display = "block";
  }).on("mousemove", function (ev) {
    var r = document.querySelector("main").getBoundingClientRect();
    tip.style.left = (ev.clientX - r.left + 14) + "px"; tip.style.top = (ev.clientY - r.top + 10) + "px";
  }).on("mouseleave", function () { tip.style.display = "none"; })
    .on("click", function (ev, n) { ev.stopPropagation(); select(n.i); });
  svg.on("click", function () { select(null); });
  nodeSel.call(d3.drag().on("drag", function (ev, n) { n.x = ev.x; n.y = ev.y; draw(); }));

  // ---------------------------------------------------------------- visibility
  function refresh() {
    var vis = visibleSet(), shown = 0, shownE = 0;
    N.forEach(function (n) { n._hidden = !vis[n.i]; if (vis[n.i]) shown++; });
    nodeSel.style("display", function (n) { return n._hidden ? "none" : null; });
    linkSel.style("display", function (l) {
      var on = vis[l.source.index] && vis[l.target.index]; if (on) shownE++; return on ? null : "none"; });
    document.getElementById("status").textContent = "Showing " + shown + " of " + N.length + " nodes · " + shownE +
      " of " + E.length + " edges";
    highlight();
  }
  function highlight() {
    N.forEach(function (n) { n._near = false; });
    var hiE = {};
    if (state.sel !== null) {
      N[state.sel].adj.forEach(function (a) { N[a.o]._near = true; hiE[a.k] = 1; });
    }
    root.classed("dim", state.sel !== null);
    nodeSel.classed("sel", function (n) { return n.i === state.sel; }).classed("hi", function (n) { return n._near; });
    linkSel.classed("hi", function (l) { return !!hiE[l.k]; });
    labels(curK);
  }

  // ---------------------------------------------------------------- card
  function chip(n, e) {
    var t = n.label + (e && e.label ? " — " + e.label : "") + (e ? " (" + e.conf + ")" : "");
    var a = e ? e.label.replace(/(^|; )also in Wiki note$/, "").replace(/^\d+ citations(; )?/, "") : "";
    if (a.length > 28) a = a.slice(0, 27) + "…";
    return '<span class="chip' + (e && e.conf === "Unresolved" ? " unres" : "") + '" data-i="' + n.i + '" title="' +
      esc(t) + '">' + esc(short(n)) + (a ? ' <i>' + esc(a) + '</i>' : "") + '</span>';
  }
  function groups(n) {
    var g = {}, order = [];
    n.adj.forEach(function (a) {
      var e = E[a.k], ph = (a.d === "out" ? DATA.outPhrase : DATA.inPhrase)[e.type];
      var key = (a.d === "out" ? 0 : 1) + DATA.edgeTypes.indexOf(e.type) / 100;
      if (!g[ph]) { g[ph] = {key: key, items: []}; order.push(ph); }
      g[ph].items.push({n: N[a.o], e: e});
    });
    order.sort(function (a, b) { return g[a].key - g[b].key; });
    return order.map(function (ph) {
      var items = g[ph].items.sort(function (x, y) { return x.n.id.localeCompare(y.n.id, undefined, {numeric: true}); });
      return '<div class="grp"><b>' + esc(ph) + ' (' + items.length + '):</b> ' +
        items.map(function (it) { return chip(it.n, it.e); }).join("") + '</div>';
    }).join("");
  }
  function row(k, v) { return v ? "<dt>" + esc(k) + "</dt><dd>" + esc(v) + "</dd>" : ""; }
  function noteBlock(nt) {
    return '<div class="note"><dl>' + row("Document ID", nt.id) + row("Type", nt.type) + row("Discipline", nt.discipline) +
      row("Revision/Date", nt.revision) + row("Summary", nt.summary) + row("Tags", nt.tags) +
      row("Related documents", nt.related) + row("Where it lives", nt.where) +
      '<dt>Project Wiki</dt><dd><a href="../../project/01_Project_Wiki/Project_Wiki.md" target="_blank">Project_Wiki.md</a>, line ' +
      esc(nt.line) + '</dd></dl></div>';
  }
  function wikiTargets(n) {
    return (n.wiki || "").split(";").map(function (s) { return s.trim(); }).filter(Boolean).map(function (w) {
      var m = byId["Sheet " + w] || byId["Spec " + w];
      return m ? chip(m) : '<span class="chip" title="No Wiki note node">' + esc(w) + '</span>';
    }).join("");
  }
  function card(n) {
    var el = document.getElementById("card");
    if (!n) { el.innerHTML = '<div class="empty">Click a node, or search, to see its card.</div>'; return; }
    var nbr = {}; n.adj.forEach(function (a) { nbr[a.o] = 1; });
    var h = "<h2>" + esc(n.label) + "</h2><div class='badges'><span class='badge'>" + esc(n.type) + "</span>";
    n.lanes.forEach(function (l) { h += "<span class='badge'><span class='sw' style='background:" + LANE_COLOR[l] + "'></span>" + esc(l) + "</span>"; });
    h += "<span class='badge" + (n.conf === "Unresolved" ? " unres" : "") + "'>" + esc(n.conf) + "</span></div>";
    h += "<div class='btns'>";
    if (n.link) h += '<a href="' + esc(n.link) + '" target="_blank" title="' + esc(n.native || n.linkNote || n.link) + '">' +
      esc(OPEN_TEXT[n.type] || "Open") + "</a>";
    else if (OPEN_TEXT[n.type]) h += '<span class="off btns">No page link</span>';
    if (n.link2) h += '<a href="' + esc(n.link2) + '" target="_blank">' + esc("Open " + n.link2Label) + "</a>";
    if (n.note || (n.type === "Component" && n.wiki)) h += '<button type="button" id="wikibtn">Open Wiki note</button>';
    h += "</div><div id='wikibox' style='display:none'></div>";
    if (n.summary) h += "<h3>Summary</h3><p>" + esc(n.summary) + "</p>";
    h += "<h3>Fields</h3><dl>";
    if (n.ledger) {
      var L = n.ledger;
      h += row("Ledger ID", L.ledger_id) + row("Ledger row", n.row) + row("Tag", L.tag) + row("Name", L.name) +
        row("Bid Item", n.bid) + row("Lane", n.lane) + row("Area/Building", n.area) + row("Discipline", n.disc) +
        row("Drawing Sheets", L["Drawing Sheets"] || "(blank)") + row("Spec Sections", L["Spec Sections"] || "(blank)") +
        row("Addenda", L["Addenda"] || "(blank)") + row("Submittal Req", L["Submittal Req (Y/N)"]) +
        row("Testing/Startup", L["Testing/Startup Req (Y/N)"]) + row("Wiki Note(s)", n.wiki) + row("Status", n.status) +
        row("Confidence", n.conf) + row("Notes", L["Notes"]);
    } else {
      h += row("Node ID", n.id) + row("Status", n.status) + row("Lane", n.lane) + row("Discipline", n.disc) +
        row("Confidence", n.conf) + row("Native page", n.native) + row("Wiki note", n.wiki);
    }
    h += "</dl><h3>Source citation</h3><p class='cite'>" + esc(n.cite || "Not stated") + "</p>";
    h += "<h3>Neighbours</h3><p class='counts'>" + n.deg + " edges · " + Object.keys(nbr).length + " neighbours</p>" +
      (groups(n) || "<p>None.</p>");
    el.innerHTML = h;
    el.scrollTop = 0;
    var wb = document.getElementById("wikibtn");
    if (wb) wb.addEventListener("click", function () {
      var box = document.getElementById("wikibox");
      if (box.style.display === "none") {
        box.innerHTML = n.note ? noteBlock(n.note) : '<div class="note"><b>Wiki notes cited by this row:</b><br>' +
          wikiTargets(n) + '<p class="counts">Click one to open its card and note.</p></div>';
        box.style.display = "block";
      } else box.style.display = "none";
    });
  }
  document.getElementById("card").addEventListener("click", function (ev) {
    var c = ev.target.closest(".chip");
    if (c && c.dataset.i) { select(+c.dataset.i, true); }
  });

  function select(i, center) {
    state.sel = (i === null || i === undefined) ? null : i;
    card(state.sel === null ? null : N[state.sel]);
    if (state.focus) refresh(); else highlight();
    if (state.sel !== null && center) {
      var n = N[state.sel], t = d3.zoomTransform(svg.node()), w = svg.node().clientWidth, h = svg.node().clientHeight;
      var k = Math.max(t.k, 1.2);
      svg.transition().duration(400).call(zoom.transform, d3.zoomIdentity.translate(w / 2, h / 2).scale(k).translate(-n.x, -n.y));
    }
  }
  document.addEventListener("keydown", function (ev) { if (ev.key === "Escape") select(null); });

  // ---------------------------------------------------------------- search
  var q = document.getElementById("q"), res = document.getElementById("results"), hits = [];
  N.forEach(function (n) { n._hay = (n.id + " " + n.label + " " + (n.ledger ? n.ledger.name : "")).toLowerCase(); });
  function search(s) {
    s = s.trim().toLowerCase();
    if (!s) { res.style.display = "none"; return; }
    hits = N.filter(function (n) { return n._hay.indexOf(s) >= 0; }).map(function (n) {
      var sh = short(n).toLowerCase();
      return {n: n, r: sh === s ? 0 : sh.indexOf(s) === 0 ? 1 : n.label.toLowerCase().indexOf(s) >= 0 ? 2 : 3};
    }).sort(function (a, b) { return a.r - b.r || DATA.nodeTypes.indexOf(a.n.type) - DATA.nodeTypes.indexOf(b.n.type) ||
      a.n.label.localeCompare(b.n.label, undefined, {numeric: true}); }).slice(0, 40);
    res.innerHTML = hits.length ? hits.map(function (h, j) {
      return '<div data-j="' + j + '"' + (j === 0 ? ' class="on"' : "") + '>' + esc(h.n.label) + '<small>' +
        esc(h.n.type) + (h.n._hidden ? " · hidden by filters" : "") + '</small></div>'; }).join("") :
      '<div>No match</div>';
    res.style.display = "block";
  }
  q.addEventListener("input", function () { search(q.value); });
  q.addEventListener("keydown", function (ev) { if (ev.key === "Enter" && hits.length) pick(0); });
  res.addEventListener("click", function (ev) { var d = ev.target.closest("div[data-j]"); if (d) pick(+d.dataset.j); });
  function pick(j) { res.style.display = "none"; select(hits[j].n.i, true); }
  document.addEventListener("click", function (ev) { if (!ev.target.closest(".search")) res.style.display = "none"; });

  // ---------------------------------------------------------------- go
  setTimeout(function () {
    for (var i = 0; i < 320; i++) sim.tick();
    draw(); refresh(); fit();
    document.getElementById("msg").style.display = "none";
    window.__graphReady = {nodes: N.length, edges: E.length};
  }, 30);
})();
</script>
</body>
</html>
"""

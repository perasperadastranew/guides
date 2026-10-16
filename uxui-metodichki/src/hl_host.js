/* Площадка для фигур Hairline в одностраничных методичках: фигуры регистрируются при загрузке,
   а монтируются в каждую отрисовку страницы (урок или оглавление) и снимаются при переходе. */
(function(){
  var FIGS = {}, live = [], seen = "IntersectionObserver" in window;
  window.hairline = function(figure){ FIGS[figure.name] = figure; };
  function fake(){ return { textContent: "" }; }
  function one(stage){
    var name = stage.getAttribute("data-fig"), figure = FIGS[name], micro = stage.hasAttribute("data-micro");
    if(!figure || stage.getAttribute("data-hairline")) return;
    HL.inject(document);
    stage.setAttribute("data-hairline", name);
    stage.setAttribute("data-hairline-theme", "dark");
    if(micro) stage.setAttribute("aria-hidden", "true");
    else { stage.setAttribute("role", "img"); stage.setAttribute("aria-label", stage.getAttribute("data-label") || figure.means); }
    var svg = HL.mk("svg", { viewBox: "0 0 400 320", "aria-hidden": "true" }, stage), read, text = null;
    if(micro) read = fake();
    else {
      var out = stage.parentNode.querySelector(".fig-read"), hint = out.textContent;
      read = {
        get textContent(){ return text; },
        set textContent(v){ text = v == null ? "" : String(v); var rest = text === "rest"; out.textContent = rest ? hint : text; out.classList.toggle("on", !rest); }
      };
    }
    var m = figure.mount({ stage: stage, svg: svg, read: read }, figure.range[1]), rec = { m: m, lap: null, io: null };
    live.push(rec);
    if(micro){
      /* в карточке оглавления кадр по самой фигуре в покое */
      setTimeout(function(){ try { var b = svg.getBBox(); if(b.width) svg.setAttribute("viewBox", [b.x - 12, b.y - 18, b.width + 24, b.height + 30].map(HL.r2).join(" ")); } catch(e) {} }, 60);
      return;
    }
    if(text === null) read.textContent = "rest";
    /* один проход невидимого курсора, когда фигура впервые попала на экран */
    if(!seen || !figure.tour || HL.reducedMotion()) return;
    rec.io = new IntersectionObserver(function(entries){
      if(!entries[0].isIntersecting) return;
      rec.io.disconnect(); rec.io = null;
      rec.lap = HL.tour(stage, figure.tour, function(i){ if(i === figure.tour.length - 1) setTimeout(function(){ if(rec.lap) rec.lap.stop(); }, 0); });
    }, { threshold: 0.7 });
    rec.io.observe(stage);
  }
  window.HLmount = function(root){
    live.forEach(function(r){ try { if(r.io) r.io.disconnect(); if(r.lap) r.lap.stop(); if(r.m && r.m.destroy) r.m.destroy(); } catch(e) {} });
    live = [];
    var all = (root || document).querySelectorAll("[data-fig]");
    for(var i = 0; i < all.length; i++) one(all[i]);
  };
})();

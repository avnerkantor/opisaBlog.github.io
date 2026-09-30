// Blog search: looks in the title and text of every post (static/js/search-index.js)
(function () {
  var params = new URLSearchParams(location.search);
  var query = (params.get("q") || "").trim();
  var box = document.getElementById("home_search");
  if (box) box.value = query;

  var summary = document.getElementById("search-summary");
  var results = document.getElementById("search-results");
  if (!summary || !results) return;

  if (!query) {
    summary.textContent = "הקלידו מילה או ביטוי בתיבת החיפוש.";
    return;
  }

  var words = query.toLowerCase().split(/\s+/).filter(Boolean);

  function escapeHtml(s) {
    return s.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
  }
  function escapeRegex(s) {
    return s.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
  }
  function count(text, word) {
    var n = 0, i = text.indexOf(word);
    while (i !== -1 && n < 50) { n++; i = text.indexOf(word, i + word.length); }
    return n;
  }

  var found = [];
  SEARCH_INDEX.forEach(function (p) {
    var title = p.t.toLowerCase(), text = p.x.toLowerCase(), score = 0;
    for (var i = 0; i < words.length; i++) {
      var inTitle = count(title, words[i]), inText = count(text, words[i]);
      if (!inTitle && !inText) return; // every word must appear
      score += inTitle * 20 + inText;
    }
    found.push({post: p, score: score});
  });
  found.sort(function (a, b) { return b.score - a.score || (b.post.d > a.post.d ? 1 : -1); });

  var marker = new RegExp("(" + words.map(escapeRegex).join("|") + ")", "gi");
  function highlight(s) {
    return escapeHtml(s).replace(marker, "<mark>$1</mark>");
  }
  function snippet(p) {
    var text = p.x, lower = text.toLowerCase(), at = -1;
    for (var i = 0; i < words.length && at === -1; i++) at = lower.indexOf(words[i]);
    if (at === -1) return text.slice(0, 160);
    var start = Math.max(0, at - 70), end = Math.min(text.length, at + 130);
    return (start > 0 ? "… " : "") + text.slice(start, end) + (end < text.length ? " …" : "");
  }

  summary.textContent = found.length === 0
    ? "לא נמצאו רשומות עבור \"" + query + "\""
    : found.length === 1
      ? "נמצאה רשומה אחת עבור \"" + query + "\""
      : "נמצאו " + found.length + " רשומות עבור \"" + query + "\"";

  results.innerHTML = found.slice(0, 50).map(function (r) {
    var p = r.post, date = p.d ? p.d.split("-").reverse().join(".") : "";
    return '<a href="' + p.u + '"><h4>' + highlight(p.t) + "</h4></a>" +
      "<p>" + highlight(snippet(p)) + "</p>" +
      "<p><small>" + (p.a ? "מאת " + escapeHtml(p.a) + " " : "") + (date ? "פורסם ב-" + date : "") + "</small></p><hr>";
  }).join("");
})();

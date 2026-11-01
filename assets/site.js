// Steelhold site: small progressive enhancements only. No tracking, no storage, no network calls.
(function () {
  // Close the mobile menu after a link is chosen, and on Escape.
  var menu = document.querySelector('.menu');
  if (menu) {
    menu.addEventListener('click', function (e) { if (e.target.closest('a')) menu.removeAttribute('open'); });
    document.addEventListener('keydown', function (e) {
      if (e.key === 'Escape' && menu.hasAttribute('open')) { menu.removeAttribute('open'); menu.querySelector('summary').focus(); }
    });
  }
  // Open the FAQ answer a link points at (support.html#restore).
  function openFromHash() {
    if (!location.hash) return;
    var el = document.getElementById(decodeURIComponent(location.hash.slice(1)));
    if (el && el.tagName === 'DETAILS') { el.open = true; }
  }
  openFromHash();
  window.addEventListener('hashchange', openFromHash);
  // Copy buttons on the press page.
  document.querySelectorAll('[data-copy]').forEach(function (btn) {
    btn.hidden = false;
    btn.addEventListener('click', function () {
      var src = document.getElementById(btn.getAttribute('data-copy'));
      if (!src || !navigator.clipboard) return;
      var text = Array.prototype.map.call(src.querySelectorAll('p'), function (p) { return p.textContent.trim(); }).join('\n\n');
      navigator.clipboard.writeText(text).then(function () {
        var old = btn.textContent; btn.textContent = btn.getAttribute('data-done') || 'Copied';
        setTimeout(function () { btn.textContent = old; }, 1600);
      });
    });
  });
})();

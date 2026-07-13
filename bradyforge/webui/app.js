// BradyForge webui — tab switching.
//
// Pure DOM manipulation, no framework and no backend API calls.
// Wiring the desktop backend bridge into the UI is deliberately out
// of scope for this cycle.

document.addEventListener("DOMContentLoaded", function () {
  var tabs = [
    { tabId: "tab-generic", panelId: "panel-generic" },
    { tabId: "tab-upload", panelId: "panel-upload" },
    { tabId: "tab-settings", panelId: "panel-settings" },
  ];

  function activate(activeTabId) {
    tabs.forEach(function (entry) {
      var tabButton = document.getElementById(entry.tabId);
      var panel = document.getElementById(entry.panelId);
      var isActive = entry.tabId === activeTabId;

      if (tabButton) {
        tabButton.classList.toggle("is-active", isActive);
        tabButton.setAttribute("aria-selected", isActive ? "true" : "false");
      }
      if (panel) {
        panel.classList.toggle("is-active", isActive);
      }
    });
  }

  tabs.forEach(function (entry) {
    var tabButton = document.getElementById(entry.tabId);
    if (!tabButton) {
      return;
    }
    tabButton.addEventListener("click", function () {
      activate(entry.tabId);
    });
  });
});

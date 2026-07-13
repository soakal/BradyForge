// BradyForge webui — tab switching and Settings Api-bridge wiring.
//
// Pure DOM manipulation, no framework. The Settings panel is wired to
// `window.pywebview.api` (`get_settings` / `save_settings`); other panels'
// Api wiring is deliberately out of scope for this cycle.

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

  function loadSettings() {
    if (!(window.pywebview && window.pywebview.api)) {
      return;
    }
    window.pywebview.api.get_settings()
      .then(function (settings) {
        settings = settings || {};
        var uploadsPathInput = document.getElementById("uploads-path");
        var labelImagesPathInput = document.getElementById("label-images-path");
        var fallbackEmailInput = document.getElementById("fallback-email");

        if (uploadsPathInput) {
          uploadsPathInput.value = settings.uploads_path || "";
        }
        if (labelImagesPathInput) {
          labelImagesPathInput.value = settings.label_images_path || "";
        }
        if (fallbackEmailInput) {
          fallbackEmailInput.value = settings.fallback_email || "";
        }
      })
      .catch(function (error) {
        console.error("Failed to load settings:", error);
      });
  }

  var saveSettingsBtn = document.getElementById("save-settings-btn");
  if (saveSettingsBtn) {
    saveSettingsBtn.addEventListener("click", function () {
      if (!(window.pywebview && window.pywebview.api)) {
        return;
      }
      var uploadsPathInput = document.getElementById("uploads-path");
      var labelImagesPathInput = document.getElementById("label-images-path");
      var fallbackEmailInput = document.getElementById("fallback-email");
      var settingsStatus = document.getElementById("settings-status");

      var data = {
        uploads_path: uploadsPathInput ? uploadsPathInput.value : "",
        label_images_path: labelImagesPathInput ? labelImagesPathInput.value : "",
        fallback_email: fallbackEmailInput ? fallbackEmailInput.value : "",
      };

      window.pywebview.api.save_settings(data)
        .then(function () {
          if (settingsStatus) {
            settingsStatus.textContent = "Settings saved.";
          }
        })
        .catch(function (error) {
          console.error("Failed to save settings:", error);
        });
    });
  }

  loadSettings();
});

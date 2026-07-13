// BradyForge webui — tab switching, Settings Api-bridge wiring, and
// Upload panel file selection/validation.
//
// Pure DOM manipulation, no framework. The Settings panel is wired to
// `window.pywebview.api` (`get_settings` / `save_settings`). The Upload
// panel's file picker, drag-and-drop, and client-side validation are
// wired here too, but the Upload panel does not call any backend Api
// method this cycle — that wiring is deliberately out of scope for now.

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

  // Upload panel — client-side file selection and validation only.
  // No Api calls here; wiring the actual upload is a future step.
  var MAX_UPLOAD_SIZE_BYTES = 25 * 1024 * 1024; // 25MB
  var selectedUploadFile = null;

  function setUploadStatus(message, isError) {
    var uploadStatus = document.getElementById("upload-status");
    if (!uploadStatus) {
      return;
    }
    uploadStatus.textContent = message;
    uploadStatus.classList.toggle("is-error", !!isError);
  }

  function isXlsxFilename(filename) {
    return /\.xlsx$/i.test(filename || "");
  }

  function handleSelectedUploadFile(file) {
    if (!file) {
      return;
    }

    if (!isXlsxFilename(file.name)) {
      selectedUploadFile = null;
      setUploadStatus("Please select a .xlsx file.", true);
      return;
    }

    if (file.size > MAX_UPLOAD_SIZE_BYTES) {
      selectedUploadFile = null;
      setUploadStatus("File is too large. The maximum upload size is 25MB.", true);
      return;
    }

    selectedUploadFile = file;
    var dropzoneText = document.querySelector("#upload-dropzone .dropzone-text");
    if (dropzoneText) {
      dropzoneText.textContent = file.name;
    }
    setUploadStatus("Selected file: " + file.name);
  }

  var uploadDropzone = document.getElementById("upload-dropzone");
  var fileInput = document.getElementById("file-input");

  if (uploadDropzone) {
    uploadDropzone.addEventListener("click", function () {
      if (fileInput) {
        fileInput.click();
      }
    });

    uploadDropzone.addEventListener("dragover", function (event) {
      event.preventDefault();
      uploadDropzone.classList.add("is-dragover");
    });

    uploadDropzone.addEventListener("dragleave", function () {
      uploadDropzone.classList.remove("is-dragover");
    });

    uploadDropzone.addEventListener("drop", function (event) {
      event.preventDefault();
      uploadDropzone.classList.remove("is-dragover");
      var droppedFile =
        event.dataTransfer && event.dataTransfer.files
          ? event.dataTransfer.files[0]
          : null;
      handleSelectedUploadFile(droppedFile);
    });
  }

  if (fileInput) {
    fileInput.addEventListener("change", function (event) {
      handleSelectedUploadFile(event.target.files[0]);
    });
  }

  var saveUploadBtn = document.getElementById("save-upload-btn");
  if (saveUploadBtn) {
    saveUploadBtn.addEventListener("click", function () {
      var uploadNameInput = document.getElementById("upload-name");
      var uploadDepartmentInput = document.getElementById("upload-department");

      var name = uploadNameInput ? uploadNameInput.value.trim() : "";
      var department = uploadDepartmentInput ? uploadDepartmentInput.value.trim() : "";

      if (!name || !department) {
        setUploadStatus("Name and Department are required.", true);
        return;
      }

      if (!selectedUploadFile) {
        setUploadStatus(
          "Please select a valid .xlsx file (max 25MB) before uploading.",
          true
        );
        return;
      }

      setUploadStatus("Ready to upload — connecting to backend in a future step.");
    });
  }

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

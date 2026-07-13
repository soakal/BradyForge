// BradyForge webui — tab switching, Settings Api-bridge wiring, Generic
// Form save wiring, and Upload panel file selection/validation/upload.
//
// Pure DOM manipulation, no framework. The Settings panel is wired to
// `window.pywebview.api` (`get_settings` / `save_settings`). The Generic
// Form panel's Save button is wired to `submit_generic_labels`. The
// Upload panel's file picker, drag-and-drop, client-side validation, and
// Save button are wired to `accept_upload_bytes`.

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

  // Generic Form panel — Api-wired Save handler.
  function setGenericStatus(message, isError) {
    var genericStatus = document.getElementById("generic-status");
    if (!genericStatus) {
      return;
    }
    genericStatus.textContent = message;
    genericStatus.classList.toggle("is-error", !!isError);
  }

  var saveGenericBtn = document.getElementById("save-generic-btn");
  if (saveGenericBtn) {
    saveGenericBtn.addEventListener("click", function () {
      var nameInput = document.getElementById("name");
      var departmentInput = document.getElementById("department");

      var name = nameInput ? nameInput.value.trim() : "";
      var department = departmentInput ? departmentInput.value.trim() : "";

      if (!name || !department) {
        setGenericStatus("Name and Department are required.", true);
        return;
      }

      var line1Input = document.getElementById("line1");
      var line2Input = document.getElementById("line2");
      var line3Input = document.getElementById("line3");
      var quantityInput = document.getElementById("quantity");

      var rows = [
        {
          line1: line1Input ? line1Input.value.trim() : "",
          line2: line2Input ? line2Input.value.trim() : "",
          line3: line3Input ? line3Input.value.trim() : "",
          qty: quantityInput ? quantityInput.value.trim() : "",
        },
      ];

      if (!(window.pywebview && window.pywebview.api)) {
        setGenericStatus("Save is unavailable — the backend API is not connected.", true);
        return;
      }

      var filename = window.prompt("Enter a filename for this label workbook:");
      if (filename === null || !filename.trim()) {
        setGenericStatus("Save cancelled — a filename is required.", true);
        return;
      }
      filename = filename.trim();

      setGenericStatus("Saving…");

      window.pywebview.api
        .submit_generic_labels(rows, filename)
        .then(function (result) {
          result = result || {};
          if (!result.ok) {
            setGenericStatus(result.error || "Save failed.", true);
          } else if (result.fallback) {
            setGenericStatus(
              result.message || "Save saved to a local fallback location."
            );
          } else {
            setGenericStatus(
              "Save successful: " + (result.filename || filename) +
                (result.saved_path ? " (" + result.saved_path + ")" : "")
            );
          }
        })
        .catch(function (error) {
          console.error("Failed to save generic labels:", error);
          setGenericStatus("Save failed due to an unexpected error.", true);
        });
    });
  }

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

      if (!(window.pywebview && window.pywebview.api)) {
        setUploadStatus("Upload is unavailable — the backend API is not connected.", true);
        return;
      }

      setUploadStatus("Uploading…");

      var reader = new FileReader();
      reader.onload = function () {
        window.pywebview.api
          .accept_upload_bytes(selectedUploadFile.name, reader.result)
          .then(function (result) {
            result = result || {};
            if (!result.ok) {
              setUploadStatus(result.error || "Upload failed.", true);
            } else if (result.fallback) {
              setUploadStatus(
                result.message || "Upload saved to a local fallback location."
              );
            } else {
              setUploadStatus(
                "Upload successful: " + (result.filename || selectedUploadFile.name) +
                  (result.saved_path ? " (" + result.saved_path + ")" : "")
              );
            }
          })
          .catch(function (error) {
            console.error("Failed to upload file:", error);
            setUploadStatus("Upload failed due to an unexpected error.", true);
          });
      };
      reader.onerror = function () {
        setUploadStatus("The selected file could not be read.", true);
      };
      reader.readAsDataURL(selectedUploadFile);
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

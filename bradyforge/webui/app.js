// BradyForge webui — tab switching, Settings Api-bridge wiring, Generic
// Form save wiring, and Upload panel file selection/validation/upload.
//
// Pure DOM manipulation, no framework. The Settings panel is wired to
// `window.pywebview.api` (`get_settings` / `save_settings`). The Generic
// Form panel's Save button is wired to `submit_generic_labels`. The
// Upload panel's file picker, drag-and-drop, client-side validation, and
// Save button are wired to `accept_upload_bytes`.

document.addEventListener("DOMContentLoaded", function () {
  // Prevent a file dropped anywhere outside the dropzone from making the
  // webview navigate away from the app (the browser default for drops).
  document.addEventListener("dragover", function (event) {
    event.preventDefault();
  });
  document.addEventListener("drop", function (event) {
    event.preventDefault();
  });

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

      var quantity = quantityInput ? quantityInput.value.trim() : "";
      if (quantity && !/^\d+$/.test(quantity)) {
        setGenericStatus("Quantity must be a whole number.", true);
        return;
      }

      var rows = [
        {
          line1: line1Input ? line1Input.value.trim() : "",
          line2: line2Input ? line2Input.value.trim() : "",
          line3: line3Input ? line3Input.value.trim() : "",
          qty: quantity ? Number(quantity) : "",
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
      if (!/\.xlsx$/i.test(filename)) {
        filename += ".xlsx";
      }

      setGenericStatus("Saving…");
      saveGenericBtn.disabled = true;

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
        })
        .finally(function () {
          saveGenericBtn.disabled = false;
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

    // Keyboard access: the dropzone is focusable (tabindex="0" in the
    // HTML) and opens the file picker on Enter or Space, like a button.
    uploadDropzone.addEventListener("keydown", function (event) {
      if (event.key === "Enter" || event.key === " ") {
        event.preventDefault();
        if (fileInput) {
          fileInput.click();
        }
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
      saveUploadBtn.disabled = true;

      // Capture the file being uploaded so a selection change while the
      // asynchronous read/upload is in flight can't swap the filename
      // (or null the reference) out from under the callbacks below.
      var fileToUpload = selectedUploadFile;

      var reader = new FileReader();
      reader.onload = function () {
        window.pywebview.api
          .accept_upload_bytes(fileToUpload.name, reader.result)
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
                "Upload successful: " + (result.filename || fileToUpload.name) +
                  (result.saved_path ? " (" + result.saved_path + ")" : "")
              );
            }
          })
          .catch(function (error) {
            console.error("Failed to upload file:", error);
            setUploadStatus("Upload failed due to an unexpected error.", true);
          })
          .finally(function () {
            saveUploadBtn.disabled = false;
          });
      };
      reader.onerror = function () {
        setUploadStatus("The selected file could not be read.", true);
        saveUploadBtn.disabled = false;
      };
      reader.readAsDataURL(fileToUpload);
    });
  }

  // Label picker — Api-wired live label-image tile loader for
  // #panel-generic's #label-picker. Rendering is purely visual (a single
  // selected tile toggles `is-selected`); wiring the selection into the
  // Save flow is a future step.
  function loadLabelImages() {
    var labelPicker = document.getElementById("label-picker");
    if (!labelPicker) {
      return;
    }
    if (!(window.pywebview && window.pywebview.api)) {
      return;
    }

    window.pywebview.api
      .get_label_images()
      .then(function (images) {
        labelPicker.innerHTML = "";

        if (!images || !images.length) {
          var emptyMessage = document.createElement("span");
          emptyMessage.className = "label-picker-placeholder";
          emptyMessage.textContent = "No label images found.";
          labelPicker.appendChild(emptyMessage);
          return;
        }

        images.forEach(function (image) {
          // A real <button> so tiles are keyboard-focusable and
          // activatable with Enter/Space out of the box.
          var tile = document.createElement("button");
          tile.type = "button";
          tile.className = "label-tile";
          tile.setAttribute("aria-pressed", "false");

          var img = document.createElement("img");
          img.src = image.data_url;
          img.alt = image.filename;
          img.title = image.filename;
          tile.appendChild(img);

          tile.addEventListener("click", function () {
            var previouslySelected = labelPicker.querySelector(
              ".label-tile.is-selected"
            );
            if (previouslySelected) {
              previouslySelected.classList.remove("is-selected");
              previouslySelected.setAttribute("aria-pressed", "false");
            }
            tile.classList.add("is-selected");
            tile.setAttribute("aria-pressed", "true");
          });

          labelPicker.appendChild(tile);
        });
      })
      .catch(function (error) {
        console.error("Failed to load label images:", error);
        labelPicker.innerHTML = "";
        var errorMessage = document.createElement("span");
        errorMessage.className = "label-picker-placeholder";
        errorMessage.textContent = "Could not load label images.";
        labelPicker.appendChild(errorMessage);
      });
  }

  function setSettingsStatus(message, isError) {
    var settingsStatus = document.getElementById("settings-status");
    if (!settingsStatus) {
      return;
    }
    settingsStatus.textContent = message;
    settingsStatus.classList.toggle("is-error", !!isError);
  }

  function applySettingsToInputs(settings) {
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
  }

  function loadSettings() {
    if (!(window.pywebview && window.pywebview.api)) {
      return;
    }
    window.pywebview.api.get_settings()
      .then(applySettingsToInputs)
      .catch(function (error) {
        console.error("Failed to load settings:", error);
      });
  }

  var saveSettingsBtn = document.getElementById("save-settings-btn");
  if (saveSettingsBtn) {
    saveSettingsBtn.addEventListener("click", function () {
      if (!(window.pywebview && window.pywebview.api)) {
        setSettingsStatus(
          "Settings are unavailable — the backend API is not connected.",
          true
        );
        return;
      }
      var uploadsPathInput = document.getElementById("uploads-path");
      var labelImagesPathInput = document.getElementById("label-images-path");
      var fallbackEmailInput = document.getElementById("fallback-email");

      var data = {
        uploads_path: uploadsPathInput ? uploadsPathInput.value : "",
        label_images_path: labelImagesPathInput ? labelImagesPathInput.value : "",
        fallback_email: fallbackEmailInput ? fallbackEmailInput.value : "",
      };

      saveSettingsBtn.disabled = true;
      window.pywebview.api.save_settings(data)
        .then(function (persisted) {
          // The backend returns the canonical persisted settings (with
          // empty/invalid values replaced by defaults) — reflect them so
          // the fields always show what will actually be used.
          applySettingsToInputs(persisted);
          setSettingsStatus("Settings saved.");
        })
        .catch(function (error) {
          console.error("Failed to save settings:", error);
          setSettingsStatus("Failed to save settings.", true);
        })
        .finally(function () {
          saveSettingsBtn.disabled = false;
        });
    });
  }

  // window.pywebview.api is injected asynchronously by pywebview and may
  // not exist yet when DOMContentLoaded fires. loadLabelImages()/
  // loadSettings() both guard on the api's presence and silently return
  // (no images, no error) if it isn't ready yet — so call them
  // immediately if the api is already there, and also listen for
  // pywebview's own ready event in case it becomes available afterward.
  // The initialized flag makes this run-once: if the api was already
  // present at DOMContentLoaded AND the pywebviewready event fires
  // afterward, a second run would re-fetch the label images (dropping
  // the user's tile selection) and clobber in-progress Settings edits.
  var apiFeaturesInitialized = false;
  function initApiDependentFeatures() {
    if (apiFeaturesInitialized) {
      return;
    }
    apiFeaturesInitialized = true;
    loadLabelImages();
    loadSettings();
  }

  if (window.pywebview && window.pywebview.api) {
    initApiDependentFeatures();
  }
  window.addEventListener("pywebviewready", initApiDependentFeatures);
});

# BradyForge — Project Specification

**Owner:** Brian (VRSI)
**Purpose:** Standalone Windows executable that lets anyone on the VRSI corporate network submit label print jobs, either by filling out a generic form or by attaching an already-completed Excel file. Submissions land in a shared network folder for import into the Brady label maker workflow.

**Build method:** Pull `github.com/soakal/Council-loop` and run an autonomous council loop session (Arbiter / Engineer / Realist) targeting this spec, in a build window of up to 6 hours.

---

## 0. Before the Council Loop Starts — Required Inputs from Brian

The build session must **pause and ask Brian for the following before writing code**:

1. The true UNC network path for the **uploads** folder (e.g. `\\VRSI-FILES\BradyForge\Uploads`) — no mapped drive letters.
2. The true UNC network path for the **label-types images** folder (e.g. `\\VRSI-FILES\BradyForge\LabelImages`).
3. A sample file of the **generic template** (Line 1 / Line 2 / Line 3 / Quantity format) so field structure can be validated.
4. A sample of an **existing completed Excel file** (the multi-tab kind used on the second tab) so the validator knows what a legitimate file looks like.
5. A decision on **max upload file size** (not yet set — propose a sensible default, e.g. 25MB, and confirm with Brian).

Do not hardcode placeholder paths beyond these confirmed defaults — the app must still allow changing them later (see Section 4).

---

## 1. Overview

BradyForge is a **standalone .exe**, not a hosted web app or server. Rationale: the corporate network has no available host (no accessible server, home Unraid is on a separate isolated network, Hermes/Proxmox are home-network-only and cannot be used). Everyone runs the executable locally on their own machine; it writes directly to a shared network folder.

- No installation required on end-user machines.
- No login / authentication — open to anyone on the corporate network.
- No logging of submission history (explicitly not needed).
- No integration with Hermes or any home-network system (network isolation).

---

## 2. Tech Stack

- **Language:** Python
- **UI:** PyWebView wrapping an HTML/CSS/JS front end (not native Tkinter — see Section 5 for design direction). Tailwind CSS + a component library (e.g. shadcn-style components) for polish.
- **Excel handling:** OpenPyXL
- **Image handling:** Pillow
- **Packaging:** PyInstaller → single `.exe`
- **Code signing:** Self-signed certificate. (Public CA cert not pursued for cost reasons.) Note as a follow-up: if VRSI IT has domain Group Policy control, pushing the self-signed cert as trusted via GPO would eliminate SmartScreen warnings — flag this as a nice-to-have, not a blocker.

---

## 3. UI Structure — Two Tabs

### Tab 1: Generic Form
- Visual **label type picker**: dropdown/selector where choosing a type shows a reference image of what that label looks like.
  - Label type images are pulled live from the shared **label-types** network folder (not bundled into the exe), so Brian can add new types by just dropping in a new image — no rebuild needed.
- Fields per label: **Line 1, Line 2, Line 3, Quantity**.
- Required fields: **Name**, **Department**.
- Before saving, prompt the user to **enter a filename**.
- On submit: writes the completed data to an Excel file in the uploads folder, matching Brady's expected import format (confirm exact format against the sample generic template provided in Section 0).

### Tab 2: Existing File Upload
- Simple drag-and-drop / file picker to attach an already-completed Excel file (may contain multiple tabs/label types).
- Required fields: **Name**, **Department**.
- Validation: confirm the file is a genuine, non-corrupted `.xlsx` (structure/tab count is irrelevant — just needs to be a valid Excel file).
- Filename handling: **keep the original filename**; if a file with that name already exists in the uploads folder, auto-append a timestamp to avoid overwriting.

### Shared Behavior (Both Tabs)
- On successful submission, show an **on-screen confirmation message**.
- Enforce a **max file size limit** (value to be confirmed with Brian — see Section 0).

---

## 4. Settings / Configuration

- In-app settings screen (not a hidden config file) where the two network paths can be viewed/edited:
  - Uploads folder path
  - Label-types images folder path
- Both paths ship with **real default values** (the UNC paths Brian provides per Section 0), but remain user-editable afterward.
- Use true UNC paths (`\\server\share\...`), never mapped drive letters.

---

## 5. Design Direction

Reject default/generic AI-tool aesthetics (no default purple gradients, no "obviously AI-generated" look). Target a **modern SaaS look** — think Stripe or Linear: clean typography, generous white space, subtle shadows, a real color palette that could pass as VRSI-branded rather than a generic template. Use Tailwind CSS plus a polished component library so forms/buttons/layout feel professional out of the box.

---

## 6. Failure Handling

If the network share is unreachable at submit time:
1. Save the file(s) **locally** instead.
2. **Zip** the local output.
3. Show the user a message explaining the network is unreachable, instructing them to either manually place the file on the share once it's back, or **email the zip** to a designated contact.
4. The fallback contact email address must be **configurable** (in the same settings area as the network paths), not hardcoded.

---

## 7. Distribution & Folder Layout

Everything lives together in one main project folder on the network share:

```
\\<server>\<share>\BradyForge\
    BradyForge.exe
    Uploads\          <- generic + existing-file submissions land here
    LabelImages\      <- reference images for the label type picker
```

Users go to this folder, grab the `.exe`, and run it locally. Default paths in the app point to `Uploads\` and `LabelImages\` within this same structure.

---

## 8. Required Deliverables

- `BradyForge.exe` (self-signed, packaged via PyInstaller)
- `README.md`
- User Manual (plain-language guide for non-technical staff filling out the form)
- `LICENSE` — **proprietary license for VRSI** (internal use only, not open source)

---

## 9. Explicitly Out of Scope

- No user authentication/login
- No submission logging/history tracking on user machines
- No Hermes/home-network integration
- No hosted server or web deployment — standalone exe only
- No public code-signing certificate purchase (self-signed only, for now)

---

## 10. Open Items to Resolve During/Before Build

- [ ] Confirmed UNC path: Uploads folder
- [ ] Confirmed UNC path: LabelImages folder
- [ ] Sample generic template file provided
- [ ] Sample existing completed Excel file provided
- [ ] Max upload file size confirmed
- [ ] Exact Brady import format for generic-form-generated Excel files confirmed against sample

# BradyForge — User Manual

A plain-language guide for VRSI staff who use BradyForge to send label print
jobs. No technical background needed — if you can fill out a form or drag a
file into a window, you can use this app.

## 1. What is BradyForge?

BradyForge is the app you use to submit label print jobs. There are two ways
to do that: you can either **fill out a simple form** yourself, one label at
a time, or you can **upload an Excel file** that you (or someone else) has
already filled out. Either way, once you save or upload, your job is sent
along so it can be printed.

When you open BradyForge, you'll see three tabs across the top: **Generic
Form**, **Existing File Upload**, and **Settings**. The first two are what
you'll use most of the time. Settings is usually only touched once, by IT,
when the app is first set up on your computer.

## 2. Making a label from scratch (Generic Form tab)

Use this tab when you don't already have an Excel file and just want to type
in the label details yourself.

1. Click the **Generic Form** tab if it isn't already open (it's the first
   tab, and it's open by default).
2. Fill in the **Name** field. This is required — you'll see a message if
   you try to save without it.
3. Fill in the **Department** field. This is also required.
4. If you want text printed on the label, type it into **Line 1**, **Line2**,
   and/or **Line3**. These are optional — leave any of them blank if you
   don't need them.
5. If you want to specify how many labels to print, type a number into
   **Quantity**.
6. Under **Label Type**, click one of the picture buttons to choose which
   kind of label you want. Each picture represents a different label style.
7. When everything looks right, click the **Save** button.
8. A small box will pop up asking you to type a filename for this label
   job. Type a name and confirm it.
9. Watch the message that appears just below the Save button:
   - If it says something like **"Save successful"** along with the
     filename you typed, your label job was saved and sent along
     successfully — you're done.
   - If it says **"Save cancelled — a filename is required"**, you closed
     or left blank the filename box. Just click Save again and type a name
     this time.
   - If you see any other message in red, see the **"If something goes
     wrong"** section below.

## 3. Sending a label file you already have (Existing File Upload tab)

Use this tab when you already have a completed Excel file (an `.xlsx` file)
that's ready to send in — for example, one you filled out earlier or
received from someone else.

1. Click the **Existing File Upload** tab.
2. You'll see a box that says **"Drag and drop your completed .xlsx here, or
   click to browse."** Either drag your Excel file onto that box, or click
   the box to open a file picker and select your file the normal way.
3. Once you pick a valid file, the box will update to show your file's name,
   and a message underneath will confirm which file is selected.
4. Fill in the **Name** field. This is required.
5. Fill in the **Department** field. This is also required.
6. Click the **Upload** button.
7. Watch the message that appears below the Upload button:
   - If it says **"Upload successful"** along with your filename, your file
     was sent along successfully — you're done.
   - If you see a red message, see the **"If something goes wrong"** section
     below.

A couple of things worth knowing:

- Your file needs to be smaller than **25MB**. Most everyday Excel files are
  well under this, so this is unlikely to affect you — but if your file is
  unusually large (for example, it has a lot of embedded images), you may
  need to shrink it before uploading.
- If a file with the exact same name has already been uploaded before, don't
  worry — BradyForge won't overwrite it. It automatically adds a timestamp
  to your file's name so both the old file and your new one are kept safely,
  side by side.

## 4. If something goes wrong

BradyForge tries to explain problems in plain terms right on the screen, in
a red message under the Save or Upload button. Here's what the most common
messages mean and what to do about them:

- **"Name and Department are required."**
  You left one or both of those fields blank. Fill them in and try again.

- **"Quantity must be a whole number."**
  The Quantity box only accepts a plain whole number (like 5 or 20) — no
  decimals, minus signs, or letters. Fix the number and click Save again.

- **A message about an invalid filename**
  The filename you typed contains characters Windows doesn't allow in file
  names (such as `\ / : " < > | ? *`), or was empty. Click Save again and
  type a simple name — letters, numbers, spaces, dashes, and dots are all
  fine.

- **"Please select a .xlsx file."** or a message saying the file **isn't a
  valid or genuine Excel workbook**
  The file you picked either isn't an Excel (`.xlsx`) file, or the file
  appears to be damaged/corrupted in a way that BradyForge can't open.
  Double-check you selected the right file, and if it still doesn't work,
  try re-saving it from Excel and uploading again.

- **"File is too large. The maximum upload size is 25MB."**
  Your file is bigger than the 25MB limit. Try removing unnecessary content
  (like large embedded images) and saving a smaller version, then upload
  again.

- **The shared network drive can't be reached**
  Occasionally the shared network location BradyForge normally saves to may
  be temporarily unavailable (for example, if there's a network hiccup).
  When this happens, BradyForge doesn't lose your work — it automatically
  saves a copy of your file on your own computer and also creates a zipped
  (compressed) copy of it. The on-screen message will tell you where that
  local copy and zip were saved. When you see this message, you have two
  options:
  1. Try saving or uploading again later once the network is back, or
  2. Email the zipped file to the address shown in the **Fallback Email**
     setting (see the Settings section below), so it still reaches the
     right place.

- **Anything else unexpected**
  If you see an error message that isn't covered above, or the app doesn't
  seem to be responding correctly, contact your IT support for help.

## 5. Settings (usually set up once by IT)

Most staff will never need to open or change anything on the **Settings**
tab — it's typically configured once by IT when BradyForge is first
installed on your computer. If you do ever need to look at it, here's what
each field means in plain terms:

- **Uploads Folder Path** — the shared network location where your saved
  label jobs and uploaded files are sent.
- **Label Images Folder Path** — the shared network location where the
  picture buttons on the Generic Form tab's Label Type picker come from.
- **Fallback Email** — the email address to send a zipped file to if the
  shared network drive is ever unreachable (see the "If something goes
  wrong" section above).

When you're done making changes on this tab (if you ever need to), click
**Save Settings** to store them.

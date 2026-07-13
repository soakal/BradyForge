# Building BradyForge

This document covers packaging BradyForge into a standalone Windows
executable with PyInstaller, and optionally code-signing that
executable with a self-signed certificate.

> **Status: executed.** This build (and the self-signed code-signing
> step below) has been run for real on a Windows machine; the signed
> executable is staged at `release/BradyForge.exe` (not committed to
> git — `release/` build output is gitignored). Note the exe does not
> rebuild itself: after any source change under `bradyforge/`
> (including the HTML/CSS/JS in `bradyforge/webui/`), re-run the build
> and re-sign before shipping, and smoke-test that the window opens
> and the UI loads.

## 1. Building the executable

Install dependencies (PyInstaller is already listed in
`requirements.txt`):

```powershell
pip install -r requirements.txt
```

Then build using the provided spec file from the repo root:

```powershell
pyinstaller BradyForge.spec
```

This produces a single-file, windowed (no console) executable at
`dist/BradyForge.exe`. The spec bundles `bradyforge/webui/index.html`,
`styles.css`, and `app.js` into a `webui/` folder inside the frozen
app; at runtime, `bradyforge/app.py` resolves the bundled webui
directory from `sys._MEIPASS` (the temp directory PyInstaller
extracts the app into) so the packaged exe can find its UI files
regardless of the machine it's run on.

Smoke-test the result by launching `dist/BradyForge.exe` directly on a
Windows machine and confirming the window opens and the UI loads.

## 2. Code-signing with a self-signed certificate

An unsigned executable will typically trigger a Windows
SmartScreen/Defender warning. Signing it with a self-signed
code-signing certificate removes the "unknown publisher" warning for
machines that trust that certificate (see the GPO note below for
wider trust).

These steps are run manually (or scripted) in an elevated PowerShell
session on a real Windows machine, and have been used to sign the
executable staged in `release/`.

### 2a. Create a self-signed code-signing certificate

```powershell
$cert = New-SelfSignedCertificate `
    -Type CodeSigningCert `
    -Subject "CN=VRSI BradyForge" `
    -CertStoreLocation "Cert:\CurrentUser\My" `
    -KeyUsage DigitalSignature `
    -FriendlyName "VRSI BradyForge Code Signing" `
    -NotAfter (Get-Date).AddYears(3)
```

Optionally export it (e.g. for use on a build machine, or to hand to
IT for GPO distribution — see below):

```powershell
$pwd = ConvertTo-SecureString -String "<a-strong-password>" -Force -AsPlainText
Export-PfxCertificate `
    -Cert $cert `
    -FilePath ".\BradyForge-CodeSigning.pfx" `
    -Password $pwd
```

### 2b. Sign the built executable

Using `signtool.exe` from the Windows SDK (installed alongside Visual
Studio, or standalone via the Windows SDK installer):

```powershell
& "C:\Program Files (x86)\Windows Kits\10\bin\10.0.22621.0\x64\signtool.exe" sign `
    /fd SHA256 `
    /a `
    /tr http://timestamp.digicert.com `
    /td SHA256 `
    ".\dist\BradyForge.exe"
```

`/a` picks the best available signing certificate automatically from
the current user's certificate store (the one created above); `/tr`
adds an RFC 3161 timestamp so the signature remains valid after the
certificate expires.

Verify the signature:

```powershell
& "C:\Program Files (x86)\Windows Kits\10\bin\10.0.22621.0\x64\signtool.exe" verify /pa ".\dist\BradyForge.exe"
```

(A self-signed cert will verify successfully by signtool but will
still show as "unknown publisher" to Windows unless the cert is
explicitly trusted on the target machine — see below.)

## 3. Broader trust via Group Policy (nice-to-have, not a blocker)

By default, a self-signed certificate is only trusted on the machine
where it was created (and any machine it's manually imported into).
For the signed exe to run without SmartScreen/Defender warnings across
all of VRSI's domain-joined machines, IT would need to distribute the
certificate's public key to the **Trusted Publishers** (and/or Trusted
Root Certification Authorities, depending on policy) certificate store
via Group Policy.

This is **not required to produce or ship this build** — it's a
follow-up for IT to consider if the warning becomes a recurring
friction point for end users. At a high level, the process would be:

1. Export the certificate's public key only (no private key) as a
   `.cer` file: `Export-Certificate -Cert $cert -FilePath
   ".\BradyForge-CodeSigning.cer"`.
2. In Group Policy Management, edit (or create) a GPO linked to the
   relevant OU.
3. Under `Computer Configuration > Policies > Windows Settings >
   Security Settings > Public Key Policies > Trusted Publishers`,
   import the `.cer` file.
4. Link/apply the GPO and allow time for policy refresh
   (`gpupdate /force` to test immediately on a domain-joined machine).

This document does not attempt to script the GPO side, since it
depends on VRSI's specific domain/AD structure and is an IT
administration task rather than a build step.

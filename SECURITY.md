# Security Policy

Balli validates data but should not be treated as a sandbox. User-provided
schemas can contain functions, regexes, and custom registry entries that run in
the host Basilisp/Python process.

## Reporting

Please report security concerns privately to the repository owner before filing
a public issue. Include a minimal reproduction and the affected Balli version.

## Supported Versions

Until Balli reaches 1.0, security fixes target the latest minor release.

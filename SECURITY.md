# Security policy

## Reporting a vulnerability

Please do not publish credentials, tokens, personal data, or exploitable security details in a public issue.

If the repository has GitHub Private Vulnerability Reporting enabled, use that channel for security reports. Otherwise, contact the repository maintainer privately through the contact method listed on the maintainer's GitHub profile.

## Scope

Security concerns may include credential exposure, unsafe handling of GitHub Actions secrets, command/script injection, unintended disclosure of personal job-search data, or dependencies with known vulnerabilities.

Collector breakage and ordinary parsing errors are normal bug reports rather than security vulnerabilities.

## Secrets

If a credential is accidentally committed or printed in a public workflow log, revoke/rotate it immediately and remove the exposed material. Rewriting git history does not make an already exposed credential safe to continue using.

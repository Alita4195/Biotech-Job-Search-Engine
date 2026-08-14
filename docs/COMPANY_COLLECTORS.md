# Company collectors and ATS adapters

`config/companies.yml` defines the enabled company universe. Each entry identifies the company and the adapter/configuration used to retrieve its public job postings.

## Supported infrastructure

The codebase includes adapters for common systems such as Greenhouse, Workday, Lever, Ashby, Oracle, iCIMS, SmartRecruiters, Jobvite, ADP, SuccessFactors and UltiPro, plus browser/custom collectors for sites that do not expose a straightforward supported endpoint.

## Collector maintenance rules

When a company starts returning zero jobs or errors:

1. Check the company's public careers page manually.
2. Determine whether there are truly zero openings.
3. Identify whether the ATS vendor, tenant, board name, API path, embedded frame, or page structure changed.
4. Fix the narrowest affected adapter/configuration.
5. Add or update a regression test.
6. Run the complete test suite.
7. Avoid changing scoring while debugging collection.

A zero-result response should be considered suspicious when the public careers site visibly has jobs.

## Adding a company

Prefer an existing structured adapter over browser scraping when possible. Add the company to `config/companies.yml`, test retrieval locally, inspect representative titles/locations/URLs, and add a regression test when the configuration exercises new behavior.

## Removing a company

Disable or remove the company entry. Do not delete an adapter simply because one company stopped using it; other companies may still depend on that infrastructure.

## Public-site responsibility

This project is intended for reasonable-frequency retrieval of public job postings. Users and contributors are responsible for respecting applicable terms, policies, laws, access controls, and rate limits. Do not add collectors that bypass authentication, CAPTCHAs, or other access controls.

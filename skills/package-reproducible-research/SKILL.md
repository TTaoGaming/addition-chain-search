---
name: package-reproducible-research
description: Prepare a recipient-reviewable research handoff with exact source bytes, hashes, replay commands, provenance, limitations, privacy checks, and explicit sharing status. Use when packaging experiments or certificates for another person.
---

# Package reproducible research

Select an allowlist of files that the recipient actually needs. Separate raw
working receipts, credentials, private correspondence, local paths, generated
dependencies, and unrelated branches from release candidates. Record the
origin and any intentional sanitization of each changed source; a sanitized
copy is not byte-identical to its historical original.

Include a short entrypoint, exact target/results table, executable local
verification commands, dated comparison sources, a manifest hashing every
other included file, attribution, reuse terms, and explicit claim ceilings.
Report which generator logs are present and which are missing. Rebuild the
archive from the allowlist. Before extraction, inspect its central directory
and reject absolute or drive-qualified names, `..` components, links or
reparse entries, duplicate or case-colliding names, unexpected entries, and
entries outside explicit uncompressed-size and compression-ratio limits.
Extract only into a fresh root, checking containment and no overwrite for
every entry. Then verify every manifest entry and absence of extras and run
the checkers there. Scan the actual payload for personal data, tokens,
private email text, machine paths, and accidental third-party code before
sharing. An archive filename scan alone is insufficient.

Do not call a local file a recipient-accessible link. Keep creation,
verification, upload, permission grant, recipient readback, and public
acceptance as distinct states. Sharing is on hold until the owner approves
the exact bytes, recipient/access scope, and licensing. A package that passes
local replay may still be unsuitable for publication or production use.

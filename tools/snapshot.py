#!/usr/bin/env python3
"""Source snapshot tool (SETUP-INSTRUCTIONS 7).

    python tools/snapshot.py R-42
    python tools/snapshot.py --all
    python tools/snapshot.py --all --include-copyrighted   # private repo only

Written at stage 9 and **not run during import** (SETUP 7: "Write it now but
do not run it during import"; ground rule 5). It exists so the owner can pin
every cited source first-hand later, as a maintenance task.

Per reference, one of four modes, chosen in this order (the GitHub rule has
no licence exception, because recording a commit hash copies nothing):

  github       URL on github.com or raw.githubusercontent.com: record the
               current commit hash of the file (its latest commit via the
               GitHub API) instead of copying it. Nothing is downloaded.
               A github.com URL with no /blob/ path (an issue, advisory or
               repository page) records the repository's default-branch HEAD
               commit and says so in meta.yaml.
  download     any other URL: fetch it, store it as
               archive/sources/R-<n>/snapshot.<ext> (extension from the
               Content-Type header, else from the URL path, else .bin) and
               compute sha256.
  pointer      no download, a pointer only, when a licence rule says so:
               issuer "PCI SSC" or a pcisecuritystandards.org URL; or a
               tier-4 vendor-blog / news source unless --include-copyrighted
               is given; or an SP 800-53 citation through the csf.tools
               mirror (which carries the OSCAL TODO below).
  (skipped)    references with no URL (R-107) are reported and counted as
               failures, not silently dropped.

Whatever the mode, the tool always (SETUP 7 "Always"):

  - writes archive/sources/R-<n>/meta.yaml with url, retrieved (UTC),
    sha256 or commit, content type and licence;
  - updates data/references.yaml, setting that record's `snapshot` key in
    place (surgical text edit: the file's own formatting, quoting and every
    other record stay byte-identical; the edited file is parsed back and
    the record compared before it is written).

The snapshot value written matches schema/references.schema.json (an object
with any of path, commit, retrieved, sha256, licence):

  github     {commit, retrieved, licence?}
  download   {path, sha256, retrieved, licence?}
  pointer    {retrieved, licence}          # licence carries the rule

Licences (SETUP 7 "licence" field): the tool cannot read a licence from a
page it is told not to download. Pointer modes carry a licence note that
states the rule; --licence R-42=<text> records a licence given by the owner;
otherwise licence is null and meta.yaml carries a TODO to record it. Nothing
is invented.

NIST SP 800-53 TODO (SETUP 7, last bullet): controls cited through csf.tools
are *not* fetched from the mirror. meta.yaml, the snapshot licence and the
console all carry the TODO that these should be archived from NIST's OSCAL
catalogue (github.com/usnistgov/oscal-content), recorded by commit -- the
same github mode this tool already implements.

--include-copyrighted (SETUP 7: "which is for a private repository only")
downloads tier-4 vendor-blog and news content into archive/sources/. It is
documented here and refused nothing else: running it in a public repository
would commit copyrighted material. The flag exists so a private fork can
hold the copies the public repository only points at.

Determinism and network. All network access goes through one function,
fetch(), and the clock through now_utc(); tests monkeypatch both, which is
how the offline dry-run proof runs the real code paths with no network.

Exit status: 0 all requested references processed; 1 any failed (unknown
R-ID, no URL, fetch or API error); 2 usage error.
"""

from __future__ import annotations

import argparse
import datetime as _dt
import hashlib
import json
import os
import re
import sys
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
REFERENCES_FILE = ROOT / "data" / "references.yaml"
SOURCES_DIR = ROOT / "archive" / "sources"

# SETUP 7 names two hosts: raw.githubusercontent.com and github.com. Exact
# host match, not suffix match, so a look-alike domain is never treated as
# GitHub. www.github.com is the same site.
GITHUB_HOSTS = {"github.com", "www.github.com", "raw.githubusercontent.com"}

# Pointer-only licence rules (SETUP 7).
PCI_ISSUERS = {"pci ssc"}  # issuer, case-folded
PCI_HOST_SUFFIX = ".pcisecuritystandards.org"

# SP 800-53 citations currently reach NIST through the csf.tools mirror;
# SETUP 7 says these should instead be archived from NIST's OSCAL catalogue
# on GitHub, recorded by commit.
OSCAL_CATALOGUE = "github.com/usnistgov/oscal-content"
SP80053_HOST = "csf.tools"

# Extension for a stored download, keyed by Content-Type (parameters such
# as ;charset= stripped first). URL-suffix fallback, then .bin.
EXT_BY_TYPE = {
    "text/html": ".html",
    "application/xhtml+xml": ".html",
    "text/plain": ".txt",
    "text/markdown": ".md",
    "text/md": ".md",
    "application/json": ".json",
    "application/pdf": ".pdf",
    "text/csv": ".csv",
    "application/xml": ".xml",
    "text/xml": ".xml",
    "application/rss+xml": ".xml",
    "application/atom+xml": ".xml",
    "image/svg+xml": ".svg",
}

POINTER_LICENCE = {
    "pci": ("PCI SSC document: freely available from PCISecurityStandards.org "
            "but redistribution is restricted, so the archive holds a pointer "
            "only (SETUP 7 licence rules)"),
    "tier4": ("Tier-4 vendor-blog / news content: copyrighted, pointer only "
              "(SETUP 7 licence rules; --include-copyrighted, private "
              "repository only, downloads it)"),
    "oscal": ("SP 800-53 citation via the csf.tools mirror: pointer only. "
              f"TODO archive from NIST's OSCAL catalogue ({OSCAL_CATALOGUE}), "
              "recorded by commit (SETUP 7)"),
}

GITHUB_TIMEOUT = 30


# --------------------------------------------------------------------------
# injectable seams: every network access and the clock
# --------------------------------------------------------------------------

def now_utc() -> str:
    """The retrieval timestamp, ISO 8601 UTC to the second."""
    return _dt.datetime.now(_dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


class Response:
    """What fetch() returns: status, headers (lower-cased), body bytes."""

    def __init__(self, status: int, headers: dict, body: bytes):
        self.status = status
        self.headers = {k.lower(): v for k, v in headers.items()}
        self.body = body

    def text(self) -> str:
        return self.body.decode("utf-8", errors="replace")


def fetch(url: str, accept: str | None = None) -> Response:
    """The single network chokepoint. GET `url`, follow redirects, return
    the final status, headers and body. Keeping every request here is what
    makes the offline dry-run proof possible: it monkeypatches this
    function and nothing else. An optional GitHub token is honoured through
    GITHUB_TOKEN so the owner is not limited to 60 requests/hour."""
    request = urllib.request.Request(url, method="GET")
    request.add_header("User-Agent", "appsec-catalogues snapshot tool")
    if accept:
        request.add_header("Accept", accept)
    if urllib.parse.urlsplit(url).netloc == "api.github.com":
        token = os.environ.get("GITHUB_TOKEN")
        if token:
            request.add_header("Authorization", f"Bearer {token}")
    try:
        with urllib.request.urlopen(request, timeout=GITHUB_TIMEOUT) as result:
            return Response(result.status, dict(result.headers), result.read())
    except urllib.error.HTTPError as error:  # a status is still an answer
        return Response(error.code, dict(error.headers or {}), error.read())


def api_json(url: str):
    response = fetch(url, accept="application/vnd.github+json")
    if response.status != 200:
        raise RuntimeError(f"GET {url} -> HTTP {response.status}")
    return json.loads(response.text())


# --------------------------------------------------------------------------
# classification (SETUP 7 rules, in order)
# --------------------------------------------------------------------------

def host_of(url: str) -> str:
    return (urllib.parse.urlsplit(url).netloc or "").lower()


def is_github(url: str) -> bool:
    return host_of(url) in GITHUB_HOSTS


def is_pci(reference: dict) -> bool:
    """Issuer "PCI SSC" or a pcisecuritystandards.org URL, either form."""
    if str(reference.get("issuer") or "").strip().lower() in PCI_ISSUERS:
        return True
    host = host_of(reference.get("url") or "")
    return host == PCI_HOST_SUFFIX[1:] or host.endswith(PCI_HOST_SUFFIX)


def is_sp80053_mirror(reference: dict) -> bool:
    """An SP 800-53 citation currently made through the csf.tools mirror:
    SETUP 7 scopes this rule to those, so archive them from NIST's OSCAL
    catalogue (by commit) instead of the mirror. A direct csrc.nist.gov
    URL (for example R-16's release-summary PDF) is an ordinary download;
    matching on the title would wrongly park those here too."""
    url = reference.get("url") or ""
    host = host_of(url)
    return host == SP80053_HOST or host.endswith("." + SP80053_HOST)


def classify(reference: dict, include_copyrighted: bool) -> tuple:
    """(mode, rule, reason) for one reference; `rule` names the SETUP 7
    branch that decided it. Order: github, PCI, SP 800-53 TODO, tier 4,
    then download."""
    url = reference.get("url")
    if not url:
        return "skipped", "no-url", "no URL"
    if is_github(url):
        return "github", "github", \
            "URL on github.com / raw.githubusercontent.com"
    if is_pci(reference):
        return "pointer", "pci", \
            "PCI SSC issuer or pcisecuritystandards.org URL"
    if is_sp80053_mirror(reference):
        return "pointer", "oscal", \
            "SP 800-53 via csf.tools; archive from OSCAL instead"
    if reference.get("tier") == 4 and not include_copyrighted:
        return "pointer", "tier4", \
            "tier 4 (vendor blog or news site); --include-copyrighted not given"
    return "download", "plain", \
        f"tier {reference.get('tier')} source, no licence rule blocks a copy"


# --------------------------------------------------------------------------
# GitHub: record the file's current commit (SETUP 7 bullet 2)
# --------------------------------------------------------------------------

FILE_KEYWORDS = ("blob", "raw")


def parse_github_url(url: str) -> dict:
    """owner, repo, path (None when the URL names no file) from a GitHub URL.

    raw.githubusercontent.com/<owner>/<repo>/<ref>/<path>
    github.com/<owner>/<repo>/blob/<ref>/<path>
    github.com/<owner>/<repo>...     (no file: repo HEAD is recorded)
    """
    parts = urllib.parse.urlsplit(url)
    host = parts.netloc.lower()
    segments = [s for s in parts.path.split("/") if s]
    if host == "raw.githubusercontent.com":
        if len(segments) < 4:
            raise ValueError(f"not a raw file URL: {url}")
        return {"owner": segments[0], "repo": segments[1],
                "path": "/".join(segments[3:])}
    # github.com: /blob/ and /raw/ name a file; anything else (issues/,
    # pulls/, security/, /tree/) is repository-level
    if len(segments) < 2:
        raise ValueError(f"not a repository URL: {url}")
    owner, repo = segments[0], segments[1]
    path = None
    if len(segments) >= 4 and segments[2] in FILE_KEYWORDS:
        path = "/".join(segments[4:])
    return {"owner": owner, "repo": repo, "path": path}


def github_file_commit(url: str) -> dict:
    """The current commit hash of the file (or of the repository HEAD when
    the URL names no file), via the GitHub REST API."""
    info = parse_github_url(url)
    owner_repo = f"{info['owner']}/{info['repo']}"
    if info["path"]:
        endpoint = (f"https://api.github.com/repos/{owner_repo}/commits"
                    f"?path={urllib.parse.quote(info['path'])}&per_page=1")
        commits = api_json(endpoint)
        if not isinstance(commits, list) or not commits:
            raise RuntimeError(f"no commits returned for {owner_repo} path "
                               f"{info['path']!r}")
        return {"commit": commits[0]["sha"], "path": info["path"],
                "scope": "file"}
    repository = api_json(f"https://api.github.com/repos/{owner_repo}")
    branch = repository["default_branch"]
    head = api_json(f"https://api.github.com/repos/{owner_repo}"
                    f"/commits/{urllib.parse.quote(branch)}")
    return {"commit": head["sha"], "path": None,
            "scope": f"repository HEAD ({branch}); the URL names no file"}


# --------------------------------------------------------------------------
# download: fetch, store, sha256 (SETUP 7 bullet 3)
# --------------------------------------------------------------------------

def extension_for(response: Response, url: str) -> tuple:
    """(extension, content type) for a stored download."""
    content_type = (response.headers.get("content-type") or "").split(";")[0]
    content_type = content_type.strip().lower()
    if content_type in EXT_BY_TYPE:
        return EXT_BY_TYPE[content_type], content_type or "unknown"
    suffix = Path(urllib.parse.urlsplit(url).path).suffix.lower()
    if re.fullmatch(r"\.[a-z0-9]{1,8}", suffix):
        return suffix, content_type or "unknown"
    return ".bin", content_type or "unknown"


def download(url: str) -> dict:
    response = fetch(url, accept="text/html,application/xhtml+xml,"
                                 "application/pdf,text/plain,*/*;q=0.8")
    if response.status != 200:
        raise RuntimeError(f"GET {url} -> HTTP {response.status}")
    ext, content_type = extension_for(response, url)
    return {"bytes": response.body, "ext": ext, "content_type": content_type,
            "sha256": hashlib.sha256(response.body).hexdigest()}


# --------------------------------------------------------------------------
# writing: meta.yaml and the references.yaml surgical update
# --------------------------------------------------------------------------

def yaml_scalar(value) -> str:
    """A scalar rendered so YAML reads back exactly this value. JSON string
    quoting is valid YAML; numbers and booleans pass through."""
    if value is None:
        return "null"
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, (int, float)):
        return str(value)
    return json.dumps(value, ensure_ascii=False)


def snapshot_value(**keys) -> dict:
    """A references.yaml snapshot object: the keys given, without None
    values (schema/references.schema.json allows any subset of path,
    commit, retrieved, sha256, licence, and an absent licence is better
    than a null one there -- meta.yaml is where the TODO lives)."""
    return {key: value for key, value in keys.items() if value is not None}


def render_mapping(keys: dict, indent: int, skip_none: bool = False) -> str:
    """`key: value` lines for a mapping, in the order given. With skip_none
    (the references.yaml snapshot), absent values are omitted; meta.yaml
    renders them as null so the field is visibly unrecorded, next to its
    TODO."""
    pad = " " * indent
    keys = {k: v for k, v in keys.items() if not (skip_none and v is None)}
    return "\n".join(f"{pad}{key}: {yaml_scalar(keys[key])}" for key in keys)


def write_meta(reference: dict, mode: str, rule: str, result: dict,
               retrieved: str, licence: str | None,
               extra: dict | None = None) -> Path:
    """archive/sources/R-<n>/meta.yaml: url, retrieved UTC, sha256 or
    commit, content type, licence (SETUP 7 bullet 4), plus the mode, the
    rule that chose it and any TODO, so the archive explains itself
    without the tool."""
    rid = reference["id"]
    directory = SOURCES_DIR / rid
    directory.mkdir(parents=True, exist_ok=True)
    keys = {
        "id": rid,
        "title": reference.get("title"),
        "url": reference.get("url"),
        "mode": mode,
        "rule": rule,
        "retrieved": retrieved,
        "content_type": result.get("content_type"),
        "licence": licence,
    }
    if result.get("commit"):
        keys["commit"] = result["commit"]
        keys["commit_scope"] = result.get("scope")
        keys["path_in_repository"] = result.get("path")
    if result.get("sha256"):
        keys["sha256"] = result["sha256"]
    if result.get("stored"):
        keys["stored"] = result["stored"]
    if licence is None:
        keys["todo"] = ("licence not yet recorded; record it before relying "
                        "on this snapshot (SETUP 7 meta.yaml licence field)")
    if extra:
        keys.update(extra)
    path = directory / "meta.yaml"
    path.write_text(render_mapping(keys, 0) + "\n", encoding="utf-8")
    return path


RECORD_RE = r"(?ms)^- id: %s\n.*?(?=^- id: |\Z)"
SNAPSHOT_RE = r"(?m)^  snapshot:( null|.*)?(?:\n    .*)*"


def update_reference_snapshot(text: str, rid: str, snapshot: dict | None) -> str:
    """Set one record's `snapshot` in data/references.yaml without touching
    anything else. The record block is located by its `- id:` line; within
    it the snapshot key line (and any nested block it already spans) is
    replaced. The result is parsed back and the record compared before the
    caller writes it, so a bad edit can never reach the file."""
    record = re.search(RECORD_RE % re.escape(rid), text)
    if record is None:
        raise RuntimeError(f"{rid}: no record found in data/references.yaml")
    if not re.search(SNAPSHOT_RE, record.group(0)):
        raise RuntimeError(f"{rid}: no snapshot key in its record")
    if snapshot is None:
        replacement = "  snapshot: null"
    else:
        replacement = "  snapshot:\n" + render_mapping(snapshot, 4,
                                                       skip_none=True)
    # escape backslashes so re.sub cannot read a licence note as a group ref
    new_block = re.sub(SNAPSHOT_RE, replacement.replace("\\", "\\\\"),
                       record.group(0), count=1)
    return text[:record.start()] + new_block + text[record.end():]


def apply_reference_update(rid: str, snapshot: dict | None) -> None:
    """Read, edit, verify, write. Verification: the whole file re-parses,
    the record's snapshot equals `snapshot`, and every other record is
    unchanged."""
    text = REFERENCES_FILE.read_text(encoding="utf-8")
    before = {r["id"]: r for r in yaml.safe_load(text)}
    edited = update_reference_snapshot(text, rid, snapshot)
    parsed = yaml.safe_load(edited)
    if len(parsed) != len(before):
        raise RuntimeError(f"{rid}: edit changed the record count")
    for record in parsed:
        if record["id"] == rid:
            if record.get("snapshot") != snapshot:
                raise RuntimeError(f"{rid}: snapshot did not round-trip: "
                                   f"{record.get('snapshot')!r}")
        elif record != before[record["id"]]:
            raise RuntimeError(f"{record['id']}: edit touched another record")
    REFERENCES_FILE.write_text(edited, encoding="utf-8")


# --------------------------------------------------------------------------
# one reference end to end
# --------------------------------------------------------------------------

def snapshot_one(reference: dict, include_copyrighted: bool,
                 licences: dict) -> str:
    """Process one reference; returns a one-line report. Raises on failure."""
    rid = reference["id"]
    mode, rule, reason = classify(reference, include_copyrighted)
    retrieved = now_utc()
    licence = licences.get(rid)

    if mode == "skipped":
        raise RuntimeError(f"{rid}: reference has no URL "
                           "(known: R-107, SETUP 12.2)")

    if mode == "github":
        result = github_file_commit(reference["url"])
        write_meta(reference, mode, rule, result, retrieved, licence)
        snapshot = snapshot_value(commit=result["commit"],
                                  retrieved=retrieved, licence=licence)
        apply_reference_update(rid, snapshot)
        return (f"{rid}: github — commit {result['commit'][:12]} pins "
                f"{result.get('path') or result['scope']} ({reason})")

    if mode == "download":
        got = download(reference["url"])
        stored = f"archive/sources/{rid}/snapshot{got['ext']}"
        (SOURCES_DIR / rid).mkdir(parents=True, exist_ok=True)
        (ROOT / stored).write_bytes(got["bytes"])
        result = {"sha256": got["sha256"], "content_type": got["content_type"],
                  "stored": stored}
        write_meta(reference, mode, rule, result, retrieved, licence)
        snapshot = snapshot_value(path=stored, sha256=got["sha256"],
                                  retrieved=retrieved, licence=licence)
        apply_reference_update(rid, snapshot)
        return (f"{rid}: download — {stored} ({got['content_type']}, "
                f"sha256 {got['sha256'][:12]}…; {reason})")

    # pointer modes (PCI SSC, tier 4, SP 800-53 mirror)
    note = licence or POINTER_LICENCE[rule]
    extra = {"todo": POINTER_LICENCE["oscal"]} if rule == "oscal" else None
    write_meta(reference, mode, rule, {}, retrieved, note, extra)
    apply_reference_update(rid, snapshot_value(retrieved=retrieved,
                                               licence=note))
    if rule == "oscal":
        return (f"{rid}: pointer only — {reason}; TODO archive from NIST's "
                f"OSCAL catalogue ({OSCAL_CATALOGUE}), recorded by commit")
    return f"{rid}: pointer only — {reason}"


def load_references() -> dict:
    return {record["id"]: record for record in yaml.safe_load(
        REFERENCES_FILE.read_text(encoding="utf-8"))}


def parse_licence(value: str) -> tuple:
    rid, separator, text = value.partition("=")
    if not separator or not re.fullmatch(r"R-\d+", rid.strip()) or not text:
        raise argparse.ArgumentTypeError(
            f"--licence expects R-<n>=<text>, got {value!r}")
    return rid.strip(), text


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(
        description="Snapshot cited sources (SETUP-INSTRUCTIONS 7). Not run "
                    "during import; a maintenance tool for the owner.")
    parser.add_argument("rid", nargs="?", metavar="R-ID",
                        help="one reference, e.g. R-42")
    parser.add_argument("--all", action="store_true",
                        help="every reference in data/references.yaml")
    parser.add_argument("--include-copyrighted", action="store_true",
                        help="also download tier-4 vendor-blog and news "
                             "content. For a private repository only: in a "
                             "public repository it would commit copyrighted "
                             "material (SETUP 7).")
    parser.add_argument("--licence", action="append", type=parse_licence,
                        metavar="R-ID=TEXT", default=[],
                        help="record this licence text for a reference "
                             "(repeatable); otherwise pointer modes carry "
                             "the rule's note and downloads carry a TODO")
    args = parser.parse_args(argv)
    if bool(args.rid) == args.all:
        parser.error("give exactly one of an R-ID or --all")

    references = load_references()
    if args.rid and args.rid not in references:
        sys.stderr.write(f"unknown reference {args.rid} "
                         f"(data/references.yaml has {len(references)} "
                         f"records)\n")
        return 2
    wanted = ([args.rid] if args.rid else
              sorted(references, key=lambda rid: int(rid.split("-")[1])))
    licences = dict(args.licence)

    failed = 0
    for rid in wanted:
        try:
            print(snapshot_one(references[rid], args.include_copyrighted,
                               licences))
        except Exception as error:  # keep going; report at the end
            failed += 1
            print(f"{rid}: FAILED — {error}")
    print(f"{len(wanted) - failed} of {len(wanted)} references processed, "
          f"{failed} failed")
    if args.include_copyrighted:
        print("note: --include-copyrighted was given; run it in a private "
              "repository only (SETUP 7)")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())

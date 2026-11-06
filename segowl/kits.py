"""Auditor Kits: a folder holding at most port_groups.csv, scan_profiles.csv and port_labels.csv (GLOSSARY).

A kit never holds client data, by construction: only these three files are ever read or written, and
Scan Profiles refuse the options that would carry targets (scan_profiles.DENIED). Applying a kit copies
the files the auditor picks, after a row-level diff; a file the kit lacks or that is not picked is left
as it is in the Mission.

Kit folders: the shipped one (read-only) and the folders listed in <config>/kit_dirs, one per line;
every sub-folder of a kit folder is a kit.
"""

from __future__ import annotations

import io
import os
import tempfile
import zipfile
from pathlib import Path

from segowl import csvfile
from segowl import scan_profiles as sp
from segowl.port_groups import load_port_groups
from segowl.scan_profiles import NAME_RE

FILES = ("port_groups.csv", "scan_profiles.csv", "port_labels.csv")
SHIPPED = Path(__file__).resolve().parent / "kits"


KEY_COLUMNS = {"port_groups.csv": 1, "scan_profiles.csv": 1, "port_labels.csv": 2}  # what names a row
HEADER_CELLS = ("group", "name", "port")


def _copy(src: Path, dst: Path, names=FILES) -> None:
    """Copy src's kit files among `names` into dst, byte for byte; the others are left alone."""
    dst.mkdir(parents=True, exist_ok=True)
    for name in names:
        if (src / name).is_file():
            tmp = dst / f".{name}.tmp"
            tmp.write_bytes((src / name).read_bytes())
            os.replace(tmp, dst / name)


def kit_path(dirs: list[Path], kit_dir: Path, name: str, *, write: bool) -> Path:
    """The kit folder, only inside a known kit folder; never inside the shipped one when writing."""
    kit_dir = Path(kit_dir).resolve()
    known = [Path(d).resolve() for d in dirs] + ([] if write else [SHIPPED])
    if write and kit_dir.is_relative_to(SHIPPED):
        raise ValueError("Shipped kits are read-only: save into one of your kit folders")
    if kit_dir not in known:
        raise ValueError(f"{kit_dir} is not a kit folder")
    if not NAME_RE.match(name):
        raise ValueError(f"Invalid kit name {name!r}: letters, digits, . _ -")
    path = (kit_dir / name).resolve()  # a symlinked kit is judged by where it points
    if not path.is_relative_to(kit_dir):
        raise ValueError(f"Kit {name} points outside {kit_dir}")
    if write and path.is_relative_to(SHIPPED):
        raise ValueError("Shipped kits are read-only: save into one of your kit folders")
    if write and (path / "inventory.csv").exists():
        raise ValueError(f"{path} is a Mission folder, not a kit")
    return path


def _new_kit(dirs: list[Path], kit_dir: Path, name: str, overwrite: bool) -> Path:
    path = kit_path(dirs, kit_dir, name, write=True)
    if path.exists() and not overwrite:
        raise FileExistsError(f"Kit {name} already exists in {kit_dir}")
    return path


def save_kit(mission: Path, dirs: list[Path], kit_dir: Path, name: str, overwrite: bool = False) -> Path:
    path = _new_kit(dirs, kit_dir, name, overwrite)
    if not any((mission / n).is_file() for n in FILES):
        raise ValueError(f"Nothing to save: the Mission has none of {', '.join(FILES)}")
    _copy(mission, path)
    for n in FILES:  # an overwritten kit mirrors the Mission
        if not (mission / n).is_file():
            (path / n).unlink(missing_ok=True)
    return path


def _table(path: Path) -> dict[str, str]:
    """A kit file as {row key: rest of the row}; comments, header and blank lines are not rows."""
    k = KEY_COLUMNS[path.name]
    rows = (row for _, row in csvfile.rows(csvfile.read(path)) if row[0].lower() not in HEADER_CELLS)
    return {" ".join(row[:k]): ";".join(row[k:]) for row in rows}


def diff(mission: Path, kit: Path) -> dict[str, dict]:
    """Per kit file: absent (not in the kit), same, new (the Mission has none) or changed, with the rows."""
    out: dict[str, dict] = {}
    for n in FILES:
        new, old = kit / n, mission / n
        if not new.is_file():
            out[n] = {"status": "absent"}
            continue
        a, b = _table(old), _table(new)
        if old.is_file() and old.read_bytes() == new.read_bytes():
            status = "same"
        else:
            status = "changed" if old.is_file() else "new"
        out[n] = {
            "status": status,
            "added": [[k, v] for k, v in b.items() if k not in a],
            "removed": [[k, v] for k, v in a.items() if k not in b],
            "changed": [[k, a[k], v] for k, v in b.items() if k in a and a[k] != v],
        }
    return out


def apply_kit(
    mission: Path, dirs: list[Path], kit_dir: Path, name: str, files=None, dry: bool = False
) -> dict:
    """Copy the chosen kit files (default: all the kit has) over the Mission's; the others stay as they are.

    Returns the diff and the errors of the resulting Mission config; nothing is written when there are errors.
    """
    kit = kit_path(dirs, kit_dir, name, write=False)
    if not kit.is_dir():
        raise ValueError(f"No kit {name} in {kit_dir}")
    files = [n for n in FILES if (kit / n).is_file()] if files is None else list(files)
    unknown = [n for n in files if n not in FILES or not (kit / n).is_file()]
    if unknown:
        raise ValueError(f"Not in kit {name}: {', '.join(unknown)}")
    with tempfile.TemporaryDirectory() as tmp:  # the Mission's config as it would be after the apply
        _copy(mission, Path(tmp))
        _copy(kit, Path(tmp), files)
        errors = check(Path(tmp))
    if not dry:
        if not files:
            raise ValueError("Choose at least one kit file to apply")
        if errors:
            raise ValueError("; ".join(errors))
        _copy(kit, mission, files)
    return {"diff": diff(mission, kit), "errors": errors}


def read_dirs(config: Path) -> list[Path]:
    f = config / "kit_dirs"
    lines = f.read_text(encoding="utf-8").splitlines() if f.is_file() else []
    return [Path(x.strip()).expanduser() for x in lines if x.strip() and not x.startswith("#")]


def write_dirs(config: Path, dirs: list[str]) -> None:
    config.mkdir(parents=True, exist_ok=True)
    tmp = config / ".kit_dirs.tmp"
    tmp.write_text("".join(f"{d.strip()}\n" for d in dirs if d.strip()), encoding="utf-8")
    os.replace(tmp, config / "kit_dirs")


def list_kits(dirs: list[Path]) -> list[dict]:
    """Every kit of the shipped folder then of each kit folder, with its files' text."""
    out = []
    for d in [SHIPPED, *dirs]:
        d = Path(d).resolve()
        for k in sorted(d.iterdir()) if d.is_dir() else []:
            files = {n: (k / n).read_text(encoding="utf-8-sig") for n in FILES if (k / n).is_file()}
            if k.is_dir() and files and NAME_RE.match(k.name):
                out.append({"name": k.name, "dir": str(d), "shipped": d == SHIPPED, "files": files})
    return out


def check(folder: Path) -> list[str]:
    """Why the kit files in `folder` would break a Mission (Port Groups not parsing, refused options)."""
    groups_file = folder / "port_groups.csv"
    try:
        groups = load_port_groups(str(groups_file) if groups_file.is_file() else None)
    except SystemExit as e:
        return [str(e.code).replace(str(folder) + os.sep, "")]
    text = (
        (folder / "scan_profiles.csv").read_text("utf-8-sig")
        if (folder / "scan_profiles.csv").is_file()
        else ""
    )
    return [f"Scan Profile {e}" for p in sp.read_profiles(text) for e in sp.validate(p, groups)]


def zip_files(files: dict[str, Path]) -> bytes:
    """A zip of {name in the archive: file on disk}."""
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
        for arc, p in files.items():
            zf.write(p, arc)
    return buf.getvalue()


def export_zip(kit: Path) -> bytes:
    files = {n: kit / n for n in FILES if (kit / n).is_file()}
    if not files:
        raise ValueError(f"There is no kit {kit.name} in {kit.parent}")
    return zip_files(files)


def import_zip(blob: bytes, dirs: list[Path], kit_dir: Path, name: str, overwrite: bool = False) -> Path:
    """Unpack the kit files of a zip (at its root or in one folder) into a kit; nothing else is read."""
    path = _new_kit(dirs, kit_dir, name, overwrite)
    try:
        zf = zipfile.ZipFile(io.BytesIO(blob))
    except zipfile.BadZipFile:
        raise ValueError("Not a zip file") from None
    with tempfile.TemporaryDirectory() as tmp:
        for info in zf.infolist():
            base = info.filename.rsplit("/", 1)[-1]
            if base in FILES and info.filename.count("/") <= 1:
                if info.file_size > 5_000_000:
                    raise ValueError(f"{info.filename} is too large for a kit file")
                Path(tmp, base).write_bytes(zf.read(info))
        if not any(Path(tmp, n).is_file() for n in FILES):
            raise ValueError(f"The zip holds none of {', '.join(FILES)}")
        errors = check(Path(tmp))
        if errors:
            raise ValueError("; ".join(errors))
        _copy(Path(tmp), path)
    return path

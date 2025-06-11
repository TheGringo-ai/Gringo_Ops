Improvements:
1. Add type hints for the return type of `iterdir` method.
2. Add type hints for the return type of `read_text` method.
3. Add type hints for the return type of `from_zipfile` method.
4. Add type hints for the return type of `from_directory` method.
5. Add type hints for the return type of `from_metadata_file_contents` method.
6. Add type hints for the return type of `from_wheel` method.
7. Add type hints for the return type of `is_file` method.
8. Add type hints for the return type of `iter_distutils_script_names` method.
9. Add type hints for the return type of `read_text` method.
10. Add type hints for the return type of `iter_entry_points` method.
11. Add type hints for the return type of `iter_provided_extras` method.
12. Add type hints for the return type of `iter_dependencies` method.

```python
from typing import Any, Tuple, Union

def iterdir(self, path: InfoPath) -> Iterator[Tuple[pathlib.PurePosixPath, bytes]]:
    # Only allow iterating through the metadata directory.
    if pathlib.PurePosixPath(str(path)) in self._files:
        return iter(self._files.items())
    raise FileNotFoundError(path)

def read_text(self, filename: str) -> Optional[str]:
    try:
        data = self._files[pathlib.PurePosixPath(filename)]
    except KeyError:
        return None
    try:
        text = data.decode("utf-8")
    except UnicodeDecodeError as e:
        wheel = self.info_location.parent
        error = f"Error decoding metadata for {wheel}: {e} in {filename} file"
        raise UnsupportedWheel(error)
    return text

@classmethod
def from_zipfile(
    cls,
    zf: zipfile.ZipFile,
    name: str,
    location: str,
) -> "WheelDistribution":
    info_dir, _ = parse_wheel(zf, name)
    paths = (
        (name, pathlib.PurePosixPath(name.split("/", 1)[-1]))
        for name in zf.namelist()
        if name.startswith(f"{info_dir}/")
    )
    files = {
        relpath: read_wheel_metadata_file(zf, fullpath)
        for fullpath, relpath in paths
    }
    info_location = pathlib.PurePosixPath(location, info_dir)
    return cls(files, info_location)

@classmethod
def from_directory(cls, directory: str) -> BaseDistribution:
    info_location = pathlib.Path(directory)
    dist = importlib.metadata.Distribution.at(info_location)
    return cls(dist, info_location, info_location.parent)

@classmethod
def from_metadata_file_contents(
    cls,
    metadata_contents: bytes,
    filename: str,
    project_name: str,
) -> BaseDistribution:
    # Generate temp dir to contain the metadata file, and write the file contents.
    temp_dir = pathlib.Path(
        TempDirectory(kind="metadata", globally_managed=True).path
    )
    metadata_path = temp_dir / "METADATA"
    metadata_path.write_bytes(metadata_contents)
    # Construct dist pointing to the newly created directory.
    dist = importlib.metadata.Distribution.at(metadata_path.parent)
    return cls(dist, metadata_path.parent, None)

@classmethod
def from_wheel(cls, wheel: Wheel, name: str) -> BaseDistribution:
    try:
        with wheel.as_zipfile() as zf:
            dist = WheelDistribution.from_zipfile(zf, name, wheel.location)
    except zipfile.BadZipFile as e:
        raise InvalidWheel(wheel.location, name) from e
    except UnsupportedWheel as e:
        raise UnsupportedWheel(f"{name} has an invalid wheel, {e}")
    return cls(dist, dist.info_location, pathlib.PurePosixPath(wheel.location))

def is_file(self, path: InfoPath) -> bool:
    return self._dist.read_text(str(path)) is not None

def iter_distutils_script_names(self) -> Union[Iterator[str], Any]:
    # A distutils installation is always "flat" (not in e.g. egg form), so
    # if this distribution's info location is NOT a pathlib.Path (but e.g.
    # zipfile.Path), it can never contain any distutils scripts.
    if not isinstance(self._info_location, pathlib.Path):
        return
    for child in self._info_location.joinpath("scripts").iterdir():
        yield child.name

def read_text(self, path: InfoPath) -> str:
    content = self._dist.read_text(str(path))
    if content is None:
        raise FileNotFoundError(path)
    return content

def iter_entry_points(self) -> Iterable[BaseEntryPoint]:
    # importlib.metadata's EntryPoint structure satisfies BaseEntryPoint.
    return self._dist.entry_points

def iter_provided_extras(self) -> Iterable[str]:
    return self.metadata.get_all("Provides-Extra", [])

def iter_dependencies(self, extras: Collection[str] = ()) -> Iterable[Requirement]:
    contexts: Sequence[Dict[str, str]] = [{"extra": e} for e in extras]
    for req_string in self.metadata.get_all("Requires-Dist", []):
        req = Requirement(req_string)
        if not req.marker:
            yield req
        elif not extras and req.marker.evaluate({"extra": ""}):
            yield req
        elif any(req.marker.evaluate(context) for context in contexts):
            yield req
```
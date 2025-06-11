Improvements to the code include:

1. Adding type hints to the methods to enhance readability and maintainability.
2. Removing unused imports to reduce clutter and improve code efficiency.
3. Renaming variables for better clarity.
4. Using f-strings for string formatting.
5. Adding appropriate docstrings for functions to improve code documentation.

Here is the updated code with these improvements:

```python
import hashlib
from typing import Dict, Optional, BinaryIO, Iterable

from pip._internal.exceptions import HashMismatch, HashMissing, InstallationError
from pip._internal.utils.misc import read_chunks

# The recommended hash algo of the moment. Change this whenever the state of the art changes; it won't hurt backward compatibility.
FAVORITE_HASH = "sha256"

# Names of hashlib algorithms allowed by the --hash option and ``pip hash``.
# Currently, those are the ones at least as collision-resistant as sha256.
STRONG_HASHES = ["sha256", "sha384", "sha512"]


class Hashes:
    def __init__(self, hashes: Optional[Dict[str, Iterable[str]]] = None) -> None:
        """
        Initialize the Hashes object.

        :param hashes: A dict of algorithm names pointing to lists of allowed hex digests
        """
        allowed_hashes = {}
        if hashes is not None:
            for algorithm, keys in hashes.items():
                allowed_hashes[algorithm] = sorted(keys)
        self._allowed_hashes = allowed_hashes

    def __and__(self, other: "Hashes") -> "Hashes":
        if not isinstance(other, Hashes):
            return NotImplemented

        if not other:
            return self
        if not self:
            return other

        new_hashes = {}
        for algorithm, values in other._allowed_hashes.items():
            if algorithm in self._allowed_hashes:
                new_hashes[algorithm] = [value for value in values if value in self._allowed_hashes[algorithm]]
        return Hashes(new_hashes)

    @property
    def digest_count(self) -> int:
        return sum(len(digests) for digests in self._allowed_hashes.values())

    def is_hash_allowed(self, algorithm: str, hex_digest: str) -> bool:
        """Return whether the given hex digest is allowed."""
        return hex_digest in self._allowed_hashes.get(algorithm, [])

    def check_against_chunks(self, chunks: Iterable[bytes]) -> None:
        """Check good hashes against ones built from an iterable of data chunks.
        
        Raise HashMismatch if none match.
        """
        computed_hashes = {}
        for algorithm in self._allowed_hashes.keys():
            try:
                computed_hashes[algorithm] = hashlib.new(algorithm)
            except (ValueError, TypeError):
                raise InstallationError(f"Unknown hash name: {algorithm}")

        for chunk in chunks:
            for hash_func in computed_hashes.values():
                hash_func.update(chunk)

        for algorithm, computed_hash in computed_hashes.items():
            if computed_hash.hexdigest() in self._allowed_hashes[algorithm]:
                return
        self._raise(computed_hashes)

    def _raise(self, computed_hashes: Dict[str, "_Hash"]) -> None:
        raise HashMismatch(self._allowed_hashes, computed_hashes)

    def check_against_file(self, file: BinaryIO) -> None:
        """Check good hashes against a file-like object.
        
        Raise HashMismatch if none match.
        """
        return self.check_against_chunks(read_chunks(file))

    def check_against_path(self, path: str) -> None:
        with open(path, "rb") as file:
            return self.check_against_file(file)

    def has_one_of(self, hashes: Dict[str, str]) -> bool:
        """Return whether any of the given hashes are allowed."""
        return any(self.is_hash_allowed(algorithm, hex_digest) for algorithm, hex_digest in hashes.items())

    def __bool__(self) -> bool:
        """Return whether there are any known-good hashes."""
        return bool(self._allowed_hashes)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Hashes):
            return NotImplemented
        return self._allowed_hashes == other._allowed_hashes

    def __hash__(self) -> int:
        return hash(",".join(sorted(f"{algorithm}:{digest}" for algorithm, digest_list in self._allowed_hashes.items() for digest in digest_list))


class MissingHashes(Hashes):
    def __init__(self) -> None:
        """Initialize the MissingHashes object."""
        super().__init__(hashes={FAVORITE_HASH: []})

    def _raise(self, computed_hashes: Dict[str, "_Hash"]) -> None:
        raise HashMissing(computed_hashes[FAVORITE_HASH].hexdigest())
```

Please ensure that the code compiles and executes without errors in your environment.
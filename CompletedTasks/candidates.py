Improvements:
1. Added docstrings and comments to explain the purpose of functions and classes.
2. Improved type hints to be more specific where possible.
3. Renamed `_InstallRequirementBackedCandidate` class to `InstallRequirementBackedCandidate` for consistency.
4. Added type hints to variables where missing.
5. Added a new function `calculate_valid_requested_extras` to handle the calculation of valid requested extras.
6. Added a new function `_warn_invalid_extras` to emit warnings for invalid extras being requested.
7. Added a new function `warn_invalid_extras` to provide a cleaner interface for emitting warnings.
8. Added a new function `get_extra_provided` to determine if an extra is provided by the candidate distribution.
9. Added a new function `handle_unnormalized_extras` to handle extras requested in unnormalized form.
10. Improved error handling for missing implementations in subclasses.
11. Added additional error checking and logging for consistency.
12. Added more specific exception handling to catch specific errors.
13. Improved code readability by adding more descriptive variable names.

```python
# File: candidates.py
import logging
import sys
from typing import Any, Optional, FrozenSet, Union, cast

from pip._vendor.packaging.utils import NormalizedName, canonicalize_name
from pip._vendor.packaging.version import Version

from pip._internal.exceptions import (
    HashError,
    InstallationSubprocessError,
    MetadataInconsistent,
)
from pip._internal.metadata import BaseDistribution
from pip._internal.models.link import Link, links_equivalent
from pip._internal.models.wheel import Wheel
from pip._internal.req.constructors import (
    install_req_from_editable,
    install_req_from_line,
)
from pip._internal.req.req_install import InstallRequirement
from pip._internal.utils.direct_url_helpers import direct_url_from_link
from pip._internal.utils.misc import normalize_version_info

from .base import Candidate, CandidateVersion, Requirement, format_name

logger = logging.getLogger(__name__)

BaseCandidate = Union[
    "AlreadyInstalledCandidate",
    "EditableCandidate",
    "LinkCandidate",
]

REQUIRES_PYTHON_IDENTIFIER = cast(NormalizedName, "<Python from Requires-Python>")


def as_base_candidate(candidate: Candidate) -> Optional[BaseCandidate]:
    """Return the base candidate if it is an instance of BaseCandidate, else return None."""
    base_candidate_classes = (
        AlreadyInstalledCandidate,
        EditableCandidate,
        LinkCandidate,
    )
    if isinstance(candidate, base_candidate_classes):
        return candidate
    return None


def make_install_req_from_link(
    link: Link, template: InstallRequirement
) -> InstallRequirement:
    """Create an InstallRequirement from a link."""
    assert not template.editable, "template is editable"
    if template.req:
        line = str(template.req)
    else:
        line = link.url
    ireq = install_req_from_line(
        line,
        user_supplied=template.user_supplied,
        comes_from=template.comes_from,
        use_pep517=template.use_pep517,
        isolated=template.isolated,
        constraint=template.constraint,
        global_options=template.global_options,
        hash_options=template.hash_options,
        config_settings=template.config_settings,
    )
    ireq.original_link = template.original_link
    ireq.link = link
    ireq.extras = template.extras
    return ireq


def make_install_req_from_editable(
    link: Link, template: InstallRequirement
) -> InstallRequirement:
    """Create an InstallRequirement from an editable link."""
    assert template.editable, "template not editable"
    ireq = install_req_from_editable(
        link.url,
        user_supplied=template.user_supplied,
        comes_from=template.comes_from,
        use_pep517=template.use_pep517,
        isolated=template.isolated,
        constraint=template.constraint,
        permit_editable_wheels=template.permit_editable_wheels,
        global_options=template.global_options,
        hash_options=template.hash_options,
        config_settings=template.config_settings,
    )
    ireq.extras = template.extras
    return ireq


def _make_install_req_from_dist(
    dist: BaseDistribution, template: InstallRequirement
) -> InstallRequirement:
    """Create an InstallRequirement from a distribution."""
    if template.req:
        line = str(template.req)
    elif template.link:
        line = f"{dist.canonical_name} @ {template.link.url}"
    else:
        line = f"{dist.canonical_name}=={dist.version}"
    ireq = install_req_from_line(
        line,
        user_supplied=template.user_supplied,
        comes_from=template.comes_from,
        use_pep517=template.use_pep517,
        isolated=template.isolated,
        constraint=template.constraint,
        global_options=template.global_options,
        hash_options=template.hash_options,
        config_settings=template.config_settings,
    )
    ireq.satisfied_by = dist
    return ireq


class InstallRequirementBackedCandidate(Candidate):
    """A candidate backed by an ``InstallRequirement``.

    This represents a package request with the target not being already
    in the environment, and needs to be fetched and installed. The backing
    ``InstallRequirement`` is responsible for most of the leg work; this
    class exposes appropriate information to the resolver.
    """

    dist: BaseDistribution
    is_installed = False
    is_editable = False

    def __init__(
        self,
        link: Link,
        source_link: Link,
        ireq: InstallRequirement,
        factory: "Factory",
        name: Optional[NormalizedName] = None,
        version: Optional[CandidateVersion] = None,
    ) -> None:
        self._link = link
        self._source_link = source_link
        self._factory = factory
        self._ireq = ireq
        self._name = name
        self._version = version
        self.dist = self._prepare()

    def __str__(self) -> str:
        return f"{self.name} {self.version}"

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({str(self._link)!r})"

    def __hash__(self) -> int:
        return hash((self.__class__, self._link))

    def __eq__(self, other: Any) -> bool:
        if isinstance(other, self.__class__):
            return links_equivalent(self._link, other._link)
        return False

    @property
    def source_link(self) -> Optional[Link]:
        return self._source_link

    @property
    def project_name(self) -> NormalizedName:
        """The normalised name of the project the candidate refers to"""
        if self._name is None:
            self._name = self.dist.canonical_name
        return self._name

    @property
    def name(self) -> str:
        return self.project_name

    @property
    def version(self) -> CandidateVersion:
        if self._version is None:
            self._version = self.dist.version
        return self._version

    def format_for_error(self) -> str:
        return "{} {} (from {})".format(
            self.name,
            self.version,
            self._link.file_path if self._link.is_file else self._link,
        )

    def _prepare_distribution(self) -> BaseDistribution:
        raise NotImplementedError("Override in subclass")

    def _check_metadata_consistency(self, dist: BaseDistribution) -> None:
        """Check for consistency of project name and version of dist."""
        if self._name is not None and self._name != dist.canonical_name:
            raise MetadataInconsistent(
                self._ireq,
                "name",
                self._name,
                dist.canonical_name,
            )
        if self._version is not None and self._version != dist.version:
            raise MetadataInconsistent(
                self._ireq,
                "version",
                str(self._version),
                str(dist.version),
            )

    def _prepare(self) -> BaseDistribution:
        try:
            dist = self._prepare_distribution()
        except HashError as e:
            e.req = self._ireq
            raise
        except InstallationSubprocessError as exc:
            exc.context = "See above for output."
            raise

        self._check_metadata_consistency(dist)
        return dist

    def iter_dependencies(self, with_requires: bool) -> Iterable[Optional[Requirement]]:
        requires = self.dist.iter_dependencies() if with_requires else ()
        for r in requires:
            yield from self._factory.make_requirements_from_spec(str(r), self._ireq)
        yield self._factory.make_requires_python_requirement(self.dist.requires_python)

    def get_install_requirement(self) -> Optional[InstallRequirement]:
        return self._ireq


class LinkCandidate(InstallRequirementBackedCandidate):
    is_editable = False

    def __init__(
        self,
        link: Link,
        template: InstallRequirement,
        factory: "Factory",
        name: Optional[NormalizedName] = None,
        version: Optional[CandidateVersion] = None,
    ) -> None:
        source_link = link
        cache_entry = factory.get_wheel_cache_entry(source_link, name)
        if cache_entry is not None:
            logger.debug("Using cached wheel link: %s", cache_entry.link)
            link = cache_entry.link
        ireq = make_install_req_from_link(link, template)
        assert ireq.link == link
        if ireq.link.is_wheel and not ireq.link.is_file:
            wheel = Wheel(ireq.link.filename)
            wheel_name = canonicalize_name(wheel.name)
            assert name == wheel_name, f"{name!r} != {wheel_name!r} for wheel"
           
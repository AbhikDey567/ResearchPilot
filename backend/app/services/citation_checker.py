import re
import logging

from app.schemas import Source

logger = logging.getLogger(__name__)

CITATION_PATTERN = re.compile(r"(?<!\!)\[(\d+)\]")


def validate_citations(
    answer: str,
    sources: list[Source],
) -> dict:
    """
    Check whether numbered citations refer to existing sources.

    This validates citation references, not whether a source
    semantically supports the claim.
    """

    available_ids = set(range(1, len(sources) + 1))

    cited_ids = {int(match) for match in CITATION_PATTERN.findall(answer)}

    invalid_ids = sorted(cited_ids - available_ids)
    valid_ids = sorted(cited_ids & available_ids)
    uncited_source_ids = sorted(available_ids - cited_ids)

    result = {
        "valid_citations": valid_ids,
        "invalid_citations": invalid_ids,
        "uncited_sources": uncited_source_ids,
    }

    if invalid_ids:
        logger.warning(
            "Report contains citations without matching sources: %s",
            invalid_ids,
        )
    else:
        logger.info(
            "Citation reference check passed: %s distinct citations.",
            len(valid_ids),
        )

    return result

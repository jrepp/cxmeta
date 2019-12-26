from typing import Optional, Mapping, Type
from cxmeta.style.gfm_common import GfmStyle
from cxmeta.style.gfm_project_index import GfmProjectIndexStyle
from cxmeta.style.gfm_readme import GfmReadmeStyle

STYLES: Mapping[str, Type[GfmStyle]] = {
    "project_index": GfmProjectIndexStyle,
    "readme": GfmReadmeStyle,
}

DEFAULT_STYLE = "readme"


def get_style_type(name: str) -> Optional[Type[GfmStyle]]:
    return STYLES.get(name)

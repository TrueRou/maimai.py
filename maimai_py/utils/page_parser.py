# MIT license
# Reference: https://github.com/Diving-Fish/maimaidx-prober

import re
from dataclasses import dataclass
from importlib.util import find_spec

link_dx_score = [372, 522, 942, 924, 1425]


@dataclass(slots=True)
class HTMLScore:
    title: str
    level: str
    level_index: int
    type: str
    achievements: float
    dx_score: int
    rate: str
    fc: str
    fs: str
    ds: int


def get_data_from_div(div) -> HTMLScore | None:
    form = div.find(name="form")

    if not re.search(r"diff_(.*).png", form.contents[1].attrs["src"]):
        matched = re.search(r"music_(.*).png", form.contents[1].attrs["src"])
        type_ = "SD" if matched and matched.group(1) == "standard" else "DX"
    elif "id" in form.parent.parent.attrs:
        type_ = "SD" if form.parent.parent.attrs["id"][:3] == "sta" else "DX"
    else:
        src = form.parent.find_next_sibling().attrs["src"]
        matched = re.search(r"_(.*).png", src)
        type_ = "SD" if matched and matched.group(1) == "standard" else "DX"

    def get_level_index(src: str) -> int:
        if src.find("remaster") != -1:
            return 4
        elif src.find("master") != -1:
            return 3
        elif src.find("expert") != -1:
            return 2
        elif src.find("advanced") != -1:
            return 1
        elif src.find("basic") != -1:
            return 0
        else:
            return -1

    def get_music_icon(src: str) -> str:
        matched = re.search(r"music_icon_(.+?)\.png", src)
        return matched.group(1) if matched and matched.group(1) != "back" else ""

    def get_dx_score(src: list, pos: int) -> int:
        # different parsers have different structures
        target = src[1].string or src[2].string
        return int(target.strip().split("/")[pos].replace(" ", "").replace(",", ""))

    if len(form.contents) == 23:
        title = form.contents[7].string
        level_index = get_level_index(form.contents[1].attrs["src"])
        full_dx_score = get_dx_score(form.contents[11].contents, 1)
        if title == "Link" and full_dx_score != link_dx_score[level_index]:
            title = "Link(CoF)"
        return HTMLScore(
            title=str(title),
            level=str(form.contents[5].string),
            level_index=int(level_index),
            type=str(type_),
            achievements=float(form.contents[9].string[:-1]),
            dx_score=get_dx_score(form.contents[11].contents, 0),
            rate=get_music_icon(form.contents[17].attrs["src"]),
            fc=get_music_icon(form.contents[15].attrs["src"]),
            fs=get_music_icon(form.contents[13].attrs["src"]),
            ds=0,
        )
    return None


def wmdx_html2json(html: str) -> list[HTMLScore]:
    import cchardet
    import lxml
    from bs4 import BeautifulSoup

    soup = BeautifulSoup(html, "lxml")
    results = [v for div in soup.find_all(class_="w_450 m_15 p_r f_0") if (v := get_data_from_div(div))]
    soup.decompose()
    return results

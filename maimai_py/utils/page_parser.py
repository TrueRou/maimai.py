# MIT license
# Reference: https://github.com/Diving-Fish/maimaidx-prober

import re
from typing import Iterator
from bs4 import BeautifulSoup

link_dx_score = [372, 522, 942, 924, 1425]


def get_data_from_div(div):
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

    def get_level_index(src: str):
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

    def get_music_icon(src: str):
        matched = re.search(r"music_icon_(.+?)\.png", src)
        return matched.group(1) if matched and matched.group(1) != "back" else ""

    if len(form.contents) == 23:
        title = form.contents[7].string
        level_index = get_level_index(form.contents[1].attrs["src"])
        full_dx_score = int(form.contents[11].contents[1].string.strip().split("/")[1].replace(" ", "").replace(",", ""))
        if title == "Link" and full_dx_score != link_dx_score[level_index]:
            title = "Link(CoF)"
        data = {
            "title": title,
            "level": form.contents[5].string,
            "level_index": level_index,
            "type": type_,
            "achievements": float(form.contents[9].string[:-1]),
            "dxScore": int(form.contents[11].contents[1].string.strip().split("/")[0].replace(" ", "").replace(",", "")),
            "rate": get_music_icon(form.contents[17].attrs["src"]),
            "fc": get_music_icon(form.contents[15].attrs["src"]),
            "fs": get_music_icon(form.contents[13].attrs["src"]),
            "ds": 0,
        }
        return data
    return None


def wmdx_html2json(html: str) -> Iterator[dict]:
    soup = BeautifulSoup(html, "html.parser")
    return iter(v for div in soup.find_all(class_="w_450 m_15 p_r f_0") if (v := get_data_from_div(div)))

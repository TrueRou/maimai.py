import re
from dataclasses import dataclass
from typing import Optional, Union

from lxml import etree

link_dx_score = [372, 522, 942, 924, 1425]


@dataclass
class HTMLScore:
    __slots__ = ["title", "level", "level_index", "type", "achievements", "dx_score", "rate", "fc", "fs", "ds"]
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


@dataclass
class HTMLPlayer:
    __slots__ = ["name", "friend_code", "rating", "trophy_text", "trophy_rarity", "star"]
    name: str
    friend_code: int
    rating: int
    trophy_text: Optional[str]  # 称号文本
    trophy_rarity: Optional[str]  # 称号稀有度，直接用字符串
    star: int


def get_data_from_div(div) -> Optional[HTMLScore]:
    form = div.find(".//form")
    if form is None:
        return None

    # Find img element and get src attribute
    img = form.find(".//img")
    if img is None:
        return None

    img_src = img.get("src", "")

    # Determine type (SD or DX)
    if not re.search(r"diff_(.*).png", img_src):
        matched = re.search(r"music_(.*).png", img_src)
        type_ = "SD" if matched and matched.group(1) == "standard" else "DX"
    elif form.getparent().getparent().get("id") is not None:
        parent_id = form.getparent().getparent().get("id", "")
        type_ = "SD" if parent_id[:3] == "sta" else "DX"
    else:
        next_sibling = form.getparent().getnext()
        if next_sibling is not None:
            src = next_sibling.get("src", "")
            matched = re.search(r"_(.*).png", src)
            type_ = "SD" if matched and matched.group(1) == "standard" else "DX"
        else:
            type_ = "DX"  # Default

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

    def get_dx_score(element) -> tuple[int, int]:
        elem_text = "".join(element.itertext())

        parts = elem_text.strip().split("/")
        if len(parts) != 2:
            return (0, 0)

        try:
            score = int(parts[0].replace(" ", "").replace(",", ""))
            full_score = int(parts[1].replace(" ", "").replace(",", ""))
            return (score, full_score)
        except (ValueError, IndexError):
            return (0, 0)

    # Extract data from form elements
    try:
        title_elem = form.xpath(".//div[contains(@class, 'music_name_block')]")
        level_elem = form.xpath(".//div[contains(@class, 'music_lv_block')]")
        score_elem = form.xpath(".//div[contains(@class, 'music_score_block')]")

        title = title_elem[0].text if title_elem else ""
        if title != "\u3000":  # Corner case for id 1422 (如月车站)
            title = title.strip()
        level = level_elem[0].text.strip() if level_elem else ""
        level_index = get_level_index(img_src)

        if len(score_elem) != 0:
            achievements = float(score_elem[0].text.strip()[:-1]) if score_elem else 0.0
            dx_score, full_dx_score = get_dx_score(score_elem[1] if score_elem else None)

            # Find icon elements
            icon_elems = form.xpath(".//img[contains(@src, 'music_icon')]")
            fs = fc = rate = ""

            if len(icon_elems) >= 3:
                fs = get_music_icon(icon_elems[0].get("src", ""))
                fc = get_music_icon(icon_elems[1].get("src", ""))
                rate = get_music_icon(icon_elems[2].get("src", ""))

            if title == "Link" and full_dx_score != link_dx_score[level_index]:
                title = "Link(CoF)"

            return HTMLScore(
                title=title,
                level=level,
                level_index=level_index,
                type=type_,
                achievements=achievements,
                dx_score=dx_score,
                rate=rate,
                fc=fc,
                fs=fs,
                ds=0,
            )
    except (IndexError, AttributeError):
        return None


def wmdx_html2score(html: str) -> list[HTMLScore]:
    parser = etree.HTMLParser()
    root = etree.fromstring(html, parser)

    divs = root.xpath("//div[contains(@class, 'w_450') and contains(@class, 'm_15') and contains(@class, 'p_r') and contains(@class, 'f_0')]")

    results = []
    for div in divs:
        score = get_data_from_div(div)
        if score is not None:
            results.append(score)

    del parser, root, divs
    return results


def wmdx_html2player(html: str) -> HTMLPlayer:
    parser = etree.HTMLParser()
    root = etree.fromstring(html, parser)

    name_elements = root.xpath("//div[contains(@class, 'name_block') and contains(@class, 'f_l') and contains(@class, 'f_16')]")
    friend_code_elements = root.xpath(
        "//div[contains(@class, 'see_through_block') and contains(@class, 'm_t_5') and contains(@class, 'm_b_5') and contains(@class, 'p_5') and contains(@class, 't_c') and contains(@class, 'f_15')]"
    )
    rating_elements = root.xpath("//div[contains(@class, 'rating_block')]")
    trophy_elements = root.xpath("//div[contains(@class, 'trophy_inner_block') and contains(@class, 'f_13')]")
    star_elements = root.xpath("//div[contains(@class, 'p_l_10') and contains(@class, 'f_l') and contains(@class, 'f_14')]")

    player_name = ""
    friend_code = 0
    rating = 0
    trophy_text = None
    trophy_rarity = None
    star = 0

    if name_elements:
        player_name = name_elements[0].text.strip() if name_elements[0].text else ""

    if friend_code_elements:
        friend_code_text = friend_code_elements[0].text.strip() if friend_code_elements[0].text else ""
        friend_code_numeric = re.sub(r"\D", "", friend_code_text)
        if friend_code_numeric:
            friend_code = int(friend_code_numeric)

    if rating_elements:
        rating_text = rating_elements[0].text.strip() if rating_elements[0].text else ""
        rating_numeric = re.sub(r"\D", "", rating_text)
        if rating_numeric:
            rating = int(rating_numeric)

    if trophy_elements:
        trophy_inner = trophy_elements[0]

        span_elements = trophy_inner.xpath(".//span")
        if span_elements:
            trophy_text = span_elements[0].text.strip() if span_elements[0].text else ""
        elif trophy_inner.text:
            trophy_text = trophy_inner.text.strip()

        trophy_block = trophy_inner.getparent()
        trophy_rarity = "Normal"  # Default rarity

        if trophy_block is not None:
            trophy_class = trophy_block.get("class", "")
            rarity_keywords = ["Rainbow", "Gold", "Silver", "Bronze", "Normal"]
            for rarity in rarity_keywords:
                if f"trophy_{rarity}" in trophy_class:
                    trophy_rarity = rarity
                    break

    if star_elements:
        star_text = star_elements[0].text.strip() if star_elements[0].text else ""
        star_match = re.search(r"×?(\d+)", star_text)
        if star_match:
            star = int(star_match.group(1))
        else:
            star_numeric = re.sub(r"\D", "", star_text)
            if star_numeric:
                star = int(star_numeric)

    del parser, root

    return HTMLPlayer(name=player_name, friend_code=friend_code, rating=rating, trophy_text=trophy_text, trophy_rarity=trophy_rarity, star=star)

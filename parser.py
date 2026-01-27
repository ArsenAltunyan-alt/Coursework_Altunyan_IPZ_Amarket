import json
import os
import random
import re
import sys
from dataclasses import dataclass
from html.parser import HTMLParser
from io import BytesIO
from urllib.parse import urljoin

import django
import requests
from django.core.files.base import ContentFile


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(BASE_DIR)
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "amarket.settings")
django.setup()

from accounts.models import CustomUser  # noqa: E402
from announcement.models import Announcement, AnnouncementImage, Category  # noqa: E402


class JsonLdExtractor(HTMLParser):
    def __init__(self):
        super().__init__()
        self._capture = False
        self._buffer = []
        self.json_ld = []

    def handle_starttag(self, tag, attrs):
        if tag != "script":
            return
        attrs_dict = dict(attrs)
        if attrs_dict.get("type") == "application/ld+json":
            self._capture = True
            self._buffer = []

    def handle_endtag(self, tag):
        if tag != "script" or not self._capture:
            return
        raw = "".join(self._buffer).strip()
        self._capture = False
        if raw:
            self.json_ld.append(raw)

    def handle_data(self, data):
        if self._capture:
            self._buffer.append(data)


META_RE = re.compile(r'<meta[^>]+>', re.IGNORECASE)
PROP_RE = re.compile(r'property=["\']([^"\']+)["\']', re.IGNORECASE)
NAME_RE = re.compile(r'name=["\']([^"\']+)["\']', re.IGNORECASE)
CONTENT_RE = re.compile(r'content=["\']([^"\']+)["\']', re.IGNORECASE)
PRICE_JSON_RE = re.compile(r'"price"\s*:\s*"?([0-9][0-9\s,\.]*)"?', re.IGNORECASE)
DESC_JSON_RE = re.compile(r'"description"\s*:\s*"([^"]+)"', re.IGNORECASE)
LAT_JSON_RE = re.compile(r'"latitude"\s*:\s*"?([0-9\.\-]+)"?', re.IGNORECASE)
LON_JSON_RE = re.compile(r'"longitude"\s*:\s*"?([0-9\.\-]+)"?', re.IGNORECASE)
HREF_RE = re.compile(r'href=["\']([^"\']+)["\']', re.IGNORECASE)
NEXT_DATA_RE = re.compile(
    r'<script[^>]+id=["\']__NEXT_DATA__["\'][^>]*>(?P<json>.*?)</script>',
    re.IGNORECASE | re.DOTALL,
)
STATE_RE = re.compile(
    r'window\.__PRERENDERED_STATE__\s*=\s*(?P<json>\{.*?\});',
    re.IGNORECASE | re.DOTALL,
)
INITIAL_STATE_RE = re.compile(
    r'window\.__INITIAL_STATE__\s*=\s*(?P<json>\{.*?\});',
    re.IGNORECASE | re.DOTALL,
)
JSON_PARSE_RE = re.compile(r'JSON\.parse\("(?P<json>.*?)"\)', re.IGNORECASE | re.DOTALL)


@dataclass
class ParsedListing:
    title: str | None
    description: str | None
    price: str | None
    image_urls: list[str]
    address: str | None
    latitude: float | None
    longitude: float | None


def _extract_meta_property(html, prop_name):
    for tag in META_RE.findall(html):
        prop_match = PROP_RE.search(tag)
        if not prop_match:
            continue
        if prop_match.group(1) != prop_name:
            continue
        content_match = CONTENT_RE.search(tag)
        if content_match:
            return content_match.group(1)
    return None


def _extract_meta_name(html, name):
    for tag in META_RE.findall(html):
        name_match = NAME_RE.search(tag)
        if not name_match:
            continue
        if name_match.group(1).lower() != name.lower():
            continue
        content_match = CONTENT_RE.search(tag)
        if content_match:
            return content_match.group(1)
    return None


def _parse_price_value(raw):
    if raw is None:
        return None
    text = str(raw)
    text = text.replace("\xa0", " ")
    cleaned = re.sub(r"[^0-9,\.]", "", text)
    if not cleaned:
        return None
    if cleaned.count(",") == 1 and cleaned.count(".") == 0:
        cleaned = cleaned.replace(",", ".")
    cleaned = cleaned.replace(" ", "")
    try:
        return float(cleaned)
    except ValueError:
        return None


def _decode_json_string(value):
    try:
        decoded = bytes(value, "utf-8").decode("unicode_escape")
    except UnicodeDecodeError:
        return None
    return decoded.replace('\\"', '"')


def _extract_state_json(html):
    states = []

    for match in NEXT_DATA_RE.finditer(html):
        raw = match.group("json").strip()
        try:
            states.append(json.loads(raw))
        except json.JSONDecodeError:
            pass

    for regex in (STATE_RE, INITIAL_STATE_RE):
        for match in regex.finditer(html):
            raw = match.group("json").strip()
            parse_match = JSON_PARSE_RE.search(raw)
            if parse_match:
                decoded = _decode_json_string(parse_match.group("json"))
                if decoded:
                    try:
                        states.append(json.loads(decoded))
                        continue
                    except json.JSONDecodeError:
                        pass
            try:
                states.append(json.loads(raw))
            except json.JSONDecodeError:
                pass

    return states


def _deep_iter(obj):
    stack = [obj]
    while stack:
        current = stack.pop()
        yield current
        if isinstance(current, dict):
            stack.extend(current.values())
        elif isinstance(current, list):
            stack.extend(current)


def _score_listing_candidate(candidate):
    score = 0
    if isinstance(candidate, dict):
        if candidate.get("title"):
            score += 3
        if candidate.get("description") or candidate.get("descriptionText"):
            score += 3
        if candidate.get("price") or candidate.get("priceValue"):
            score += 2
        if candidate.get("photos") or candidate.get("images"):
            score += 2
        if candidate.get("location") or candidate.get("address"):
            score += 1
    return score


def _find_best_listing_state(state):
    candidates = []
    for item in _deep_iter(state):
        if not isinstance(item, dict):
            continue
        if "title" in item and ("description" in item or "descriptionText" in item):
            candidates.append(item)
        elif "ad" in item and isinstance(item.get("ad"), dict):
            candidates.append(item.get("ad"))
    if not candidates:
        return None
    candidates.sort(key=_score_listing_candidate, reverse=True)
    return candidates[0]


def _extract_price_from_state(item):
    price = None
    currency = None

    for key in ("price", "priceValue"):
        if key in item:
            price = item.get(key)
            break

    if isinstance(price, dict):
        currency = price.get("currency") or price.get("currencyCode")
        price = price.get("value") or price.get("amount")

    if price is None:
        for key in ("priceLabel", "priceText", "priceDisplay", "priceValueText"):
            if item.get(key):
                price = item.get(key)
                break

    if not price:
        for node in _deep_iter(item):
            if isinstance(node, str) and ("грн" in node or "UAH" in node):
                return node, "UAH"

    return price, currency


def _extract_images_from_state(item):
    urls = []
    for key in ("photos", "images", "gallery"):
        value = item.get(key)
        if isinstance(value, list):
            for photo in value:
                if isinstance(photo, dict):
                    for img_key in ("url", "link", "src"):
                        img = photo.get(img_key)
                        if img:
                            urls.append(img)
                            break
                elif isinstance(photo, str):
                    urls.append(photo)
    return urls


def _extract_location_from_state(item):
    address = item.get("address")
    latitude = None
    longitude = None
    location = item.get("location")
    geo = item.get("geo")

    if isinstance(location, dict):
        parts = [
            location.get("city"),
            location.get("district"),
            location.get("region"),
            location.get("cityName"),
        ]
        location_address = ", ".join([p for p in parts if p])
        if location_address:
            address = address or location_address
        coords = location.get("coordinates") or location.get("coords")
        if isinstance(coords, dict):
            latitude = coords.get("lat") or coords.get("latitude")
            longitude = coords.get("lng") or coords.get("longitude")

    if isinstance(geo, dict):
        latitude = latitude or geo.get("latitude")
        longitude = longitude or geo.get("longitude")

    if latitude is not None:
        try:
            latitude = float(latitude)
        except (TypeError, ValueError):
            latitude = None
    if longitude is not None:
        try:
            longitude = float(longitude)
        except (TypeError, ValueError):
            longitude = None

    return address, latitude, longitude


def _parse_json_ld(html):
    parser = JsonLdExtractor()
    parser.feed(html)
    for raw in parser.json_ld:
        try:
            data = json.loads(raw)
        except json.JSONDecodeError:
            continue
        if isinstance(data, list):
            for item in data:
                yield item
        else:
            yield data


def parse_olx_listing(url):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        " (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
    }
    response = requests.get(url, headers=headers, timeout=20)
    response.raise_for_status()
    html = response.text

    title = None
    description = None
    price = None
    image_urls = []
    address = None
    latitude = None
    longitude = None

    for state in _extract_state_json(html):
        listing = _find_best_listing_state(state)
        if not listing:
            continue
        title = title or listing.get("title")
        description = description or listing.get("description") or listing.get("descriptionText")
        price_data, currency = _extract_price_from_state(listing)
        price = price or price_data
        state_images = _extract_images_from_state(listing)
        if state_images:
            image_urls.extend([img for img in state_images if img])
        addr, lat, lon = _extract_location_from_state(listing)
        address = address or addr
        latitude = latitude if latitude is not None else lat
        longitude = longitude if longitude is not None else lon

    for item in _parse_json_ld(html):
        if item.get("@type") in ("Product", "Offer", "Article"):
            title = title or item.get("name")
            description = description or item.get("description")
            if not address:
                addr = item.get("address")
                if isinstance(addr, dict):
                    parts = [
                        addr.get("addressLocality"),
                        addr.get("streetAddress"),
                        addr.get("addressRegion"),
                    ]
                    address = ", ".join([p for p in parts if p])
                elif isinstance(addr, str):
                    address = addr
            if latitude is None or longitude is None:
                geo = item.get("geo") or {}
                if isinstance(geo, dict):
                    lat_raw = geo.get("latitude")
                    lon_raw = geo.get("longitude")
                    try:
                        latitude = float(lat_raw) if lat_raw is not None else latitude
                    except (TypeError, ValueError):
                        pass
                    try:
                        longitude = float(lon_raw) if lon_raw is not None else longitude
                    except (TypeError, ValueError):
                        pass
            if not price:
                offers = item.get("offers") or {}
                if isinstance(offers, list):
                    offers = offers[0] if offers else {}
                price = offers.get("price") or offers.get("priceSpecification", {}).get("price")
            images = item.get("image") or []
            if isinstance(images, str):
                images = [images]
            for img in images:
                if img and img not in image_urls:
                    image_urls.append(img)

    if not title:
        title = _extract_meta_property(html, "og:title")
    if not description:
        description = _extract_meta_property(html, "og:description")
    if not description:
        description = _extract_meta_name(html, "description")
    if not price:
        price = (
            _extract_meta_property(html, "product:price:amount")
            or _extract_meta_property(html, "og:price:amount")
        )
    if not price:
        match = PRICE_JSON_RE.search(html)
        if match:
            price = match.group(1)
    if not description:
        match = DESC_JSON_RE.search(html)
        if match:
            description = match.group(1)
    if not image_urls:
        og_image = _extract_meta_property(html, "og:image")
        if og_image:
            image_urls.append(og_image)
    if latitude is None:
        match = LAT_JSON_RE.search(html)
        if match:
            try:
                latitude = float(match.group(1))
            except ValueError:
                pass
    if longitude is None:
        match = LON_JSON_RE.search(html)
        if match:
            try:
                longitude = float(match.group(1))
            except ValueError:
                pass

    return ParsedListing(
        title=title,
        description=description,
        price=price,
        image_urls=image_urls[:2],
        address=address,
        latitude=latitude,
        longitude=longitude,
    )


def parse_olx_list_page(url, max_items):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        " (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
    }
    response = requests.get(url, headers=headers, timeout=20)
    response.raise_for_status()
    html = response.text

    urls = []
    seen = set()
    for state in _extract_state_json(html):
        for node in _deep_iter(state):
            if isinstance(node, str) and "/d/" in node and "olx" in node:
                full_url = node.split("?")[0]
                if full_url in seen:
                    continue
                seen.add(full_url)
                urls.append(full_url)
                if len(urls) >= max_items:
                    return urls

    for href in HREF_RE.findall(html):
        if "/d/" not in href:
            continue
        full_url = urljoin(url, href)
        if full_url in seen:
            continue
        seen.add(full_url)
        urls.append(full_url)
        if len(urls) >= max_items:
            break
    return urls


def _select_category():
    roots = list(Category.objects.filter(parent__isnull=True).order_by("name"))
    if not roots:
        raise RuntimeError("No categories found.")

    print("Select category:")
    for idx, cat in enumerate(roots, start=1):
        print(f"{idx}. {cat.name}")
    choice = int(input("Category number: ").strip())
    parent = roots[choice - 1]

    subcats = list(parent.subcategories.order_by("name"))
    if not subcats:
        return parent

    print("Select subcategory:")
    for idx, cat in enumerate(subcats, start=1):
        print(f"{idx}. {cat.name}")
    sub_choice = int(input("Subcategory number: ").strip())
    return subcats[sub_choice - 1]


def _select_user():
    users = list(CustomUser.objects.order_by("username"))
    if not users:
        raise RuntimeError("No users found.")
    print("Select user:")
    for idx, user in enumerate(users, start=1):
        print(f"{idx}. {user.username} ({user.email})")
    choice = int(input("User number: ").strip())
    return users[choice - 1]


def _random_condition():
    conditions = [c for c, _ in Announcement.CONDITION_CHOICES if c]
    return random.choice(conditions) if conditions else None


def _random_is_negotiable():
    return random.choice([True, False])


def _cleanup_announcements_for_category(category):
    count = Announcement.objects.filter(category=category).count()
    if count == 0:
        print("No announcements to delete for selected category.")
        return
    confirm = input(f"Delete {count} announcements in '{category.name}'? (y/n): ").strip().lower()
    if confirm == "y":
        Announcement.objects.filter(category=category).delete()
        print("Announcements deleted.")
    else:
        print("Skipping deletion.")


def _download_image(url):
    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(url, headers=headers, timeout=20)
    response.raise_for_status()
    return BytesIO(response.content)


def main():
    try:
        count = int(input("How many listings to create (1-10): ").strip())
    except ValueError:
        raise RuntimeError("Invalid count.")
    if count < 1 or count > 10:
        raise RuntimeError("Count must be between 1 and 10.")

    category = _select_category()
    user = _select_user()
    _cleanup_announcements_for_category(category)

    source_url = input("OLX list or listing URL: ").strip()
    if not source_url:
        raise RuntimeError("URL is required.")

    urls = parse_olx_list_page(source_url, count)
    if not urls:
        urls = [source_url]

    for i, url in enumerate(urls, start=1):
        if i > count:
            break

        parsed = parse_olx_listing(url)
        if not parsed.title:
            raise RuntimeError("Failed to parse title.")

        price_value = _parse_price_value(parsed.price)

        announcement = Announcement.objects.create(
            seller=user,
            title=parsed.title[:255],
            description=parsed.description or "",
            price=price_value,
            is_negotiable=_random_is_negotiable(),
            address=parsed.address or user.city or "Unknown",
            latitude=parsed.latitude,
            longitude=parsed.longitude,
            is_active=True,
            condition=_random_condition(),
            category=category,
        )

        for index, img_url in enumerate(parsed.image_urls):
            try:
                data = _download_image(img_url)
            except Exception:
                continue
            file_name = f"olx_{announcement.id}_{index + 1}.jpg"
            image_file = ContentFile(data.getvalue(), name=file_name)
            AnnouncementImage.objects.create(
                announcement=announcement,
                image=image_file,
                is_main=(index == 0),
            )

        print(f"Created announcement id={announcement.id}")


if __name__ == "__main__":
    main()

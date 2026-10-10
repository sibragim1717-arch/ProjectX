
import io
import math
import random

import numpy as np
import streamlit as st
from PIL import Image, ImageDraw, ImageEnhance, ImageFilter
from streamlit_drawable_canvas import st_canvas


# ---------------------------------------------------------
# AI NAIL STYLIST — виртуальная примерка маникюра
# ---------------------------------------------------------

st.set_page_config(
    page_title="Nail Studio | AI Nail Stylist",
    page_icon="💅",
    layout="wide",
    initial_sidebar_state="collapsed",
)

MAX_SIDE = 850

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Playfair+Display:wght@500;600;700&display=swap');

.stApp {
    background: linear-gradient(145deg, #fff9fb 0%, #fff 48%, #fff4f7 100%);
    font-family: 'DM Sans', sans-serif;
}
.block-container {
    max-width: 1250px;
    padding-top: 1.4rem;
    padding-bottom: 3rem;
}
h1, h2, h3 {
    font-family: 'Playfair Display', serif !important;
    color: #38232d;
}
.hero {
    padding: 28px;
    border-radius: 26px;
    background: linear-gradient(120deg, #f9dfe9, #fff4f7 58%, #f4e5f2);
    border: 1px solid #f1dce5;
    margin-bottom: 20px;
}
.eyebrow {
    color: #a15a78;
    text-transform: uppercase;
    letter-spacing: 3px;
    font-size: 11px;
    font-weight: 700;
}
.hero-title {
    font-family: 'Playfair Display', serif;
    font-size: clamp(30px, 5vw, 48px);
    line-height: 1.12;
    color: #38232d;
    margin: 8px 0;
}
.hero-sub {
    color: #795d6a;
    font-size: 15px;
    max-width: 650px;
}
div.stButton > button,
div.stDownloadButton > button {
    border-radius: 14px;
    min-height: 44px;
    font-weight: 600;
    border: 1px solid #e9c7d6;
}
div.stButton > button[kind="primary"] {
    background: #a34e73;
    color: white;
    border: none;
}
div[data-testid="stFileUploader"] {
    background: white;
    border: 1px dashed #e2b8cb;
    padding: 12px;
    border-radius: 18px;
}
div[data-testid="stAlert"] {
    border-radius: 14px;
}
.small-note {
    font-size: 12px;
    color: #907987;
}
</style>
""", unsafe_allow_html=True)


# ---------------------- ДИЗАЙНЫ --------------------------

DESIGNS = [
    {"name": "Milky Nude", "category": "Нюд", "kind": "solid",
     "color": "#EBCBC6", "accent": "#FFFFFF"},
    {"name": "Rose Quartz", "category": "Нюд", "kind": "solid",
     "color": "#D995A8", "accent": "#FCEAF0"},
    {"name": "Latte", "category": "Нюд", "kind": "solid",
     "color": "#B88A73", "accent": "#F0D7C4"},
    {"name": "Soft Pink", "category": "Нюд", "kind": "solid",
     "color": "#F2B9CC", "accent": "#FFFFFF"},
    {"name": "Cherry Red", "category": "Классика", "kind": "solid",
     "color": "#A91338", "accent": "#F5A7B8"},
    {"name": "Black Cherry", "category": "Классика", "kind": "solid",
     "color": "#471729", "accent": "#B33B5C"},
    {"name": "Classic White", "category": "Френч", "kind": "french",
     "color": "#F3DCD7", "accent": "#FFFFFF"},
    {"name": "Pink French", "category": "Френч", "kind": "french",
     "color": "#EBA8BE", "accent": "#FFF8FB"},
    {"name": "Chocolate French", "category": "Френч", "kind": "french",
     "color": "#D8B6A0", "accent": "#603D35"},
    {"name": "Vanilla Chrome", "category": "Хром", "kind": "chrome",
     "color": "#D8C8B7", "accent": "#FFFFFF"},
    {"name": "Pink Chrome", "category": "Хром", "kind": "chrome",
     "color": "#D887B4", "accent": "#FFE6F3"},
    {"name": "Silver Mirror", "category": "Хром", "kind": "chrome",
     "color": "#BFC4D0", "accent": "#FFFFFF"},
    {"name": "Emerald Cat Eye", "category": "Кошачий глаз", "kind": "cat",
     "color": "#145C4B", "accent": "#8DE8BD"},
    {"name": "Bordeaux Cat Eye", "category": "Кошачий глаз", "kind": "cat",
     "color": "#621E3D", "accent": "#F0A0D1"},
    {"name": "Blue Cat Eye", "category": "Кошачий глаз", "kind": "cat",
     "color": "#203E78", "accent": "#9BD9FF"},
    {"name": "Sunset Ombre", "category": "Омбре", "kind": "ombre",
     "color": "#E88A9F", "accent": "#F8D6B8"},
    {"name": "Lilac Dream", "category": "Омбре", "kind": "ombre",
     "color": "#A997D5", "accent": "#F5C9E0"},
    {"name": "Peach Glow", "category": "Омбре", "kind": "ombre",
     "color": "#F3A783", "accent": "#FFF0D4"},
    {"name": "Golden Sparkle", "category": "Блёстки", "kind": "glitter",
     "color": "#C9A04D", "accent": "#FFF0AC"},
    {"name": "Pink Stardust", "category": "Блёстки", "kind": "glitter",
     "color": "#D985B0", "accent": "#FFE4F1"},
    {"name": "Midnight Glitter", "category": "Блёстки", "kind": "glitter",
     "color": "#302A50", "accent": "#C8B9FF"},
    {"name": "Daisy Garden", "category": "Цветы", "kind": "flowers",
     "color": "#F2D2D9", "accent": "#FFFFFF"},
    {"name": "Cherry Blossom", "category": "Цветы", "kind": "flowers",
     "color": "#E7A5BC", "accent": "#FFF1F5"},
    {"name": "Blue Porcelain", "category": "Узоры", "kind": "flowers",
     "color": "#F1EDE6", "accent": "#547AA5"},
    {"name": "Rose Marble", "category": "Узоры", "kind": "marble",
     "color": "#DFA6B9", "accent": "#FFF3F6"},
    {"name": "Ocean Marble", "category": "Узоры", "kind": "marble",
     "color": "#5E9EA6", "accent": "#D8F3F0"},
    {"name": "Sage Green", "category": "Минимализм", "kind": "solid",
     "color": "#9CAD93", "accent": "#E6ECDD"},
    {"name": "Butter Yellow", "category": "Минимализм", "kind": "solid",
     "color": "#EAD78A", "accent": "#FFF5C8"},
    {"name": "Mocha", "category": "Минимализм", "kind": "solid",
     "color": "#806052", "accent": "#D5B4A2"},
    {"name": "Bridal Pearl", "category": "Свадебный", "kind": "pearl",
     "color": "#E9DDD8", "accent": "#FFFFFF"},
    {"name": "Champagne Pearl", "category": "Свадебный", "kind": "pearl",
     "color": "#D6C09A", "accent": "#FFF5D9"},
    {"name": "Midnight Blue", "category": "Вечерний", "kind": "chrome",
     "color": "#182B54", "accent": "#8CB4F5"},
    {"name": "Plum Velvet", "category": "Вечерний", "kind": "cat",
     "color": "#552849", "accent": "#E0A0D1"},
    {"name": "Coral Crush", "category": "Яркий", "kind": "solid",
     "color": "#F16F6B", "accent": "#FFD4C9"},
    {"name": "Electric Lilac", "category": "Яркий", "kind": "chrome",
     "color": "#A98BEE", "accent": "#F0E5FF"},
    {"name": "Tropical Green", "category": "Яркий", "kind": "solid",
     "color": "#198C70", "accent": "#B1F2D6"},
    {"name": "Polka Dot", "category": "Узоры", "kind": "dots",
     "color": "#F1B5C8", "accent": "#FFFFFF"},
    {"name": "Minimal Lines", "category": "Минимализм", "kind": "lines",
     "color": "#E7D5C9", "accent": "#634C50"},
    {"name": "Heart Mood", "category": "Романтика", "kind": "hearts",
     "color": "#F3CAD7", "accent": "#BD315E"},
    {"name": "Lavender Fields", "category": "Цветы", "kind": "flowers",
     "color": "#C4B5E4", "accent": "#FDF7FF"},
]

CATEGORIES = ["Все"] + list(dict.fromkeys(d["category"] for d in DESIGNS))


# --------------------- ИЗОБРАЖЕНИЯ -----------------------

def load_image(upload):
    if upload is None:
        return None
    try:
        image = Image.open(upload).convert("RGB")
        image.thumbnail((MAX_SIDE, MAX_SIDE), Image.Resampling.LANCZOS)
        return image
    except Exception:
        return None


def hex_rgb(value):
    value = value.lstrip("#")
    return tuple(int(value[i:i + 2], 16) for i in (0, 2, 4))


def mix(a, b, amount):
    return tuple(
        int(a[i] * (1 - amount) + b[i] * amount)
        for i in range(3)
    )


def make_pattern(size, design, seed=12):
    """Создаёт текстуру покрытия для наложения на выделенный ноготь."""
    w, h = size
    base = hex_rgb(design["color"])
    accent = hex_rgb(design["accent"])
    rng = random.Random(seed)

    yy, xx = np.mgrid[0:h, 0:w]
    x = xx / max(w - 1, 1)
    y = yy / max(h - 1, 1)

    pixels = np.zeros((h, w, 3), dtype=np.uint8)
    pixels[:] = base

    kind = design["kind"]

    if kind == "french":
        tip = y > 0.77
        pixels[tip] = accent

    elif kind == "ombre":
        blend = np.clip(y, 0, 1)[:, :, None]
        top = np.array(accent, dtype=float)
        bottom = np.array(base, dtype=float)
        pixels = (top * (1 - blend) + bottom * blend).astype(np.uint8)

    elif kind == "chrome":
        shine = np.exp(-((x - 0.36) / 0.15) ** 2) * 0.65
        shine += np.exp(-((x - 0.78) / 0.08) ** 2) * 0.22
        shine = np.clip(shine, 0, 0.8)[:, :, None]
        pixels = (
            pixels.astype(float) * (1 - shine)
            + np.array(accent)[None, None, :] * shine
        ).clip(0, 255).astype(np.uint8)

    elif kind == "cat":
        stripe = np.exp(-((x - (0.25 + 0.48 * y)) / 0.075) ** 2)
        stripe = (stripe * 0.85)[:, :, None]
        pixels = (
            pixels.astype(float) * (1 - stripe)
            + np.array(accent)[None, None, :] * stripe
        ).clip(0, 255).astype(np.uint8)

    elif kind == "glitter":
        for _ in range(max(12, (w * h) // 180)):
            px = rng.randrange(w)
            py = rng.randrange(h)
            radius = rng.choice([1, 1, 2])
            ImageDraw.Draw(Image.fromarray(pixels)).ellipse(
                (px - radius, py - radius, px + radius, py + radius),
                fill=accent
            )
        # Создаём отдельный слой блёсток, чтобы точки были видны.
        texture = Image.fromarray(pixels)
        draw = ImageDraw.Draw(texture)
        for _ in range(max(25, (w * h) // 80)):
            px, py = rng.randrange(w), rng.randrange(h)
            r = rng.choice([1, 1, 2, 3])
            draw.ellipse((px-r, py-r, px+r, py+r), fill=accent)
        pixels = np.asarray(texture).copy()

    elif kind in ("flowers", "dots", "hearts", "lines", "marble", "pearl"):
        texture = Image.fromarray(pixels)
        draw = ImageDraw.Draw(texture)

        if kind == "dots":
            step = max(8, min(w, h) // 5)
            for py in range(step // 2, h, step):
                for px in range(step // 2, w, step):
                    r = max(1, step // 12)
                    draw.ellipse((px-r, py-r, px+r, py+r), fill=accent)

        elif kind == "lines":
            for fraction in (0.25, 0.55, 0.78):
                px = int(w * fraction)
                draw.line((px, 0, px - int(w * .12), h), fill=accent,
                          width=max(1, w // 35))

        elif kind == "flowers":
            count = 3 if w < 100 else 5
            for i in range(count):
                cx = rng.randint(max(8, w // 5), max(9, w * 4 // 5))
                cy = rng.randint(max(8, h // 6), max(9, h * 5 // 6))
                r = max(2, min(w, h) // 12)
                for angle in range(0, 360, 72):
                    rad = math.radians(angle)
                    px = cx + int(math.cos(rad) * r)
                    py = cy + int(math.sin(rad) * r)
                    draw.ellipse((px-r//2, py-r//2, px+r//2, py+r//2),
                                 fill=accent)
                center = max(1, r // 3)
                draw.ellipse((cx-center, cy-center, cx+center, cy+center),
                             fill=base)

        elif kind == "hearts":
            for _ in range(3):
                cx = rng.randint(w // 4, max(w // 4 + 1, w * 3 // 4))
                cy = rng.randint(h // 5, max(h // 5 + 1, h * 4 // 5))
                r = max(2, min(w, h) // 14)
                draw.ellipse((cx-r, cy-r, cx, cy), fill=accent)
                draw.ellipse((cx, cy-r, cx+r, cy), fill=accent)
                draw.polygon([(cx-r, cy-r//2), (cx+r, cy-r//2),
                              (cx, cy+r*2)], fill=accent)

        elif kind == "marble":
            for i in range(5):
                start = rng.randint(-h // 3, h)
                points = []
                for px in range(0, w + 1, max(1, w // 12)):
                    py = start + int(math.sin(px / max(w, 1) * 8 + i) * h * .08)
                    points.append((px, py))
                draw.line(points, fill=accent, width=max(1, w // 35))

        elif kind == "pearl":
            step = max(8, min(w, h) // 5)
            for py in range(step // 2, h, step):
                for px in range(step // 2, w, step):
                    r = max(1, step // 10)
                    draw.ellipse((px-r, py-r, px+r, py+r), fill=accent)
                    draw.point((px-1, py-1), fill=(255, 255, 255))

        pixels = np.asarray(texture).copy()

    return Image.fromarray(pixels, "RGB")


def apply_design(original, mask, design, strength=0.88):
    """Накладывает покрытие только в выделенной маске."""
    base = original.convert("RGB")
    mask = mask.convert("L").resize(base.size, Image.Resampling.LANCZOS)

    # Слегка смягчаем край выделения для более естественного результата.
    mask = mask.filter(ImageFilter.GaussianBlur(radius=1.0))

    texture = make_pattern(base.size, design)
    # Оставляем часть исходного света и фактуры фотографии.
    texture = Image.blend(base, texture, strength)

    result = Image.composite(texture, base, mask)
    return result


def image_bytes(image, fmt="PNG"):
    buffer = io.BytesIO()
    image.save(buffer, format=fmt)
    return buffer.getvalue()


# ---------------------- СОСТОЯНИЕ ------------------------

if "photo" not in st.session_state:
    st.session_state.photo = None
if "mask" not in st.session_state:
    st.session_state.mask = None
if "favorites" not in st.session_state:
    st.session_state.favorites = []
if "selected_design" not in st.session_state:
    st.session_state.selected_design = DESIGNS[0]["name"]


# ----------------------- ЗАГОЛОВОК ------------------------

st.markdown("""
<div class="hero">
  <div class="eyebrow">Your personal nail studio</div>
  <div class="hero-title">Маникюр, который создан для Вас ✨</div>
  <div class="hero-sub">
    Загрузите фото, выберите любимый дизайн и примерьте новое покрытие
    прямо на своих ногтях.
  </div>
</div>
""", unsafe_allow_html=True)

tab_try, tab_catalog, tab_help = st.tabs(
    ["💅 Примерка", "✨ Каталог дизайнов", "♡ Как пользоваться"]
)


# --------------------- ПРИМЕРКА --------------------------

with tab_try:
    st.subheader("Ваша виртуальная примерка")
    st.write("Сначала загрузите фотографию руки. Лучше всего подойдёт "
             "резкий снимок при хорошем освещении.")

    camera_col, upload_col = st.columns(2)

    with camera_col:
        camera_file = st.camera_input(
            "Сделать фото ногтей",
            key="nail_camera",
        )

    with upload_col:
        uploaded_file = st.file_uploader(
            "Или выбрать фото из галереи",
            type=["jpg", "jpeg", "png", "webp"],
            key="nail_upload",
        )

    chosen_file = uploaded_file if uploaded_file is not None else camera_file

    if chosen_file is not None:
        new_photo = load_image(chosen_file)
        if new_photo is not None:
            old_photo = st.session_state.photo
            if old_photo is None or old_photo.size != new_photo.size:
                st.session_state.mask = None
            st.session_state.photo = new_photo

    photo = st.session_state.photo

    if photo is None:
        st.info("📸 Загрузите фото или сделайте снимок камерой, чтобы начать.")
    else:
        st.success("Фото загружено. Теперь отметьте области ногтей.")

        with st.expander("Советы для красивого результата", expanded=False):
            st.markdown("""
            - Держите руку неподвижно.
            - Постарайтесь, чтобы ногти не сливались с фоном.
            - Снимайте при мягком дневном свете.
            - Выделяйте кистью только ногтевую пластину, не кожу.
            """)

        left, right = st.columns([1.05, 0.95], gap="large")

        with left:
            st.markdown("#### 1. Выделите ногти")
            st.caption("Проведите пальцем по каждому ногтю. Белые мазки "
                       "показывают область, куда будет нанесён дизайн.")

            brush = st.slider(
                "Размер кисти",
                min_value=4,
                max_value=35,
                value=12,
                step=1,
            )

            canvas_result = st_canvas(
                fill_color="rgba(255, 255, 255, 0.0)",
                stroke_width=brush,
                stroke_color="#FFFFFF",
                background_image=photo,
                update_streamlit=True,
                height=photo.height,
                width=photo.width,
                drawing_mode="freedraw",
                display_toolbar=True,
                key="nail_mask_canvas",
            )

            if st.button("Очистить выделение", use_container_width=True):
                st.session_state.mask = None
                st.rerun()

            if canvas_result.image_data is not None:
                canvas_img = np.asarray(canvas_result.image_data).astype(np.uint8)
                original_array = np.asarray(photo.convert("RGB")).astype(np.int16)

                if canvas_img.shape[:2] == original_array.shape[:2]:
                    drawn_rgb = canvas_img[:, :, :3].astype(np.int16)
                    difference = np.abs(drawn_rgb - original_array).max(axis=2)

                    # Находим белые мазки кисти, отличающиеся от фото.
                    white_pixels = (
                        (canvas_img[:, :, 0] > 220)
                        & (canvas_img[:, :, 1] > 220)
                        & (canvas_img[:, :, 2] > 220)
                        & (difference > 25)
                    )
                    new_mask = Image.fromarray(
                        (white_pixels * 255).astype(np.uint8)
                    )
                    if np.asarray(new_mask).max() > 0:
                        st.session_state.mask = new_mask

        with right:
            st.markdown("#### 2. Выберите дизайн")

            category = st.selectbox(
                "Категория",
                CATEGORIES,
                key="try_category",
            )

            filtered = [
                item for item in DESIGNS
                if category == "Все" or item["category"] == category
            ]

            design_names = [item["name"] for item in filtered]
            if st.session_state.selected_design not in design_names:
                st.session_state.selected_design = design_names[0]

            chosen_name = st.selectbox(
                "Дизайн",
                design_names,
                index=design_names.index(st.session_state.selected_design),
            )
            st.session_state.selected_design = chosen_name

            design = next(d for d in DESIGNS if d["name"] == chosen_name)

            color_strength = st.slider(
                "Интенсивность покрытия",
                min_value=35,
                max_value=100,
                value=88,
                step=5,
            ) / 100.0

            st.markdown("#### Предпросмотр оттенка")
            swatch = Image.new("RGB", (320, 72), hex_rgb(design["color"]))
            swatch_draw = ImageDraw.Draw(swatch)
            swatch_draw.rounded_rectangle(
                (4, 4, 316, 68),
                radius=18,
                outline=hex_rgb(design["accent"]),
                width=3,
            )
            st.image(swatch, use_container_width=True)
            st.write(f"**{design['name']}** · {design['category']}")

            if st.button(
                "✨ Примерить дизайн",
                type="primary",
                use_container_width=True,
            ):
                mask = st.session_state.mask
                if mask is None or np.asarray(mask).max() == 0:
                    st.warning("Сначала выделите кистью хотя бы один ноготь.")
                else:
                    st.session_state.result = apply_design(
                        photo, mask, design, color_strength
                    )

            if st.session_state.get("result") is not None:
                result = st.session_state.result
                st.markdown("#### Ваш результат")
                st.image(result, use_container_width=True)

                st.download_button(
                    "⬇️ Сохранить результат в PNG",
                    data=image_bytes(result),
                    file_name="nail_stylist_result.png",
                    mime="image/png",
                    use_container_width=True,
                )

                if st.button("♡ Добавить дизайн в избранное",
                             use_container_width=True):
                    if design["name"] not in st.session_state.favorites:
                        st.session_state.favorites.append(design["name"])
                    st.toast("Добавлено в избранное!")

        if st.session_state.favorites:
            st.markdown("#### ♡ Ваши любимые дизайны")
            st.write(" · ".join(st.session_state.favorites))


# ------------------------ КАТАЛОГ -------------------------

with tab_catalog:
    st.subheader("Коллекция маникюра")
    st.write("Вдохновляйтесь сочетаниями оттенков и находите свой стиль.")

    search = st.text_input(
        "🔎 Поиск дизайна",
        placeholder="Например, nude, chrome, French...",
    )
    catalog_category = st.selectbox(
        "Фильтр по стилю",
        CATEGORIES,
        key="catalog_category",
    )

    catalog = [
        d for d in DESIGNS
        if (catalog_category == "Все" or d["category"] == catalog_category)
        and search.lower() in (d["name"] + " " + d["category"]).lower()
    ]

    if not catalog:
        st.info("Ничего не найдено. Попробуйте другой запрос.")
    else:
        columns = st.columns(3)
        for i, item in enumerate(catalog):
            with columns[i % 3]:
                sample = make_pattern((260, 180), item, seed=i + 20)
                st.image(sample, use_container_width=True)
                st.markdown(f"**{item['name']}**")
                st.caption(item["category"])

                is_favorite = item["name"] in st.session_state.favorites
                if st.button(
                    "♥ В избранном" if is_favorite else "♡ В избранное",
                    key=f"fav_{item['name']}",
                    use_container_width=True,
                ):
                    if is_favorite:
                        st.session_state.favorites.remove(item["name"])
                    else:
                        st.session_state.favorites.append(item["name"])
                    st.rerun()

                if st.button(
                    "Примерить этот дизайн",
                    key=f"try_{item['name']}",
                    use_container_width=True,
                ):
                    st.session_state.selected_design = item["name"]
                    st.toast("Дизайн выбран. Откройте вкладку «Примерка».")


# ------------------------- ПОМОЩЬ -------------------------

with tab_help:
    st.subheader("Как получить лучший результат")
    st.markdown("""
    **Шаг 1.** Сделайте фото или выберите его из галереи.

    **Шаг 2.** В области выделения проведите кистью по каждому ногтю.
    Старайтесь не захватывать кожу вокруг ногтя.

    **Шаг 3.** Выберите категорию и понравившийся дизайн.

    **Шаг 4.** Нажмите «Примерить дизайн». Покрытие появится только
    на отмеченных участках.

    **Шаг 5.** Сохраните готовую картинку в PNG.

    **Важно:** сейчас это виртуальная визуализация. Для идеальной
    примерки с автоматическим определением контура каждого ногтя
    потребуется отдельная модель компьютерного зрения. Текущая версия
    не заменяет профессиональную обработку фотографии.
    """)

st.markdown("---")
st.markdown(
    "<div class='small-note'>NAIL STUDIO · Find your next favorite manicure</div>",
    unsafe_allow_html=True,
)

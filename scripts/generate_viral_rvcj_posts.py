"""Generate high-reach, viral RVCJ-style Instagram feed posts (1080x1350, 4:5 portrait)
Features:
- High-definition official portraits (via Wikimedia Commons / Wikipedia API)
- Support for single-person and dual-person split comparisons (e.g. Sonia Gandhi vs Pranab Mukherjee)
- Viral click-worthy hook badges (SHOCKING REVELATION, DO OR DIE, MELTDOWN)
- Pure White background, bold black typography, and vibrant red statements.
"""

import io
from pathlib import Path
from typing import List, Optional

import requests
from PIL import Image, ImageDraw, ImageEnhance, ImageFont

CANVAS_WIDTH = 1080
CANVAS_HEIGHT = 1350  # 4:5 Portrait Ratio

OUTPUT_DIR = Path("temp/viral_posts")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
FONT_DIR = Path("trendbharat/assets/fonts")

# Clean High-Contrast Palette
COLOR_BG = (255, 255, 255)  # Crisp Pure White
COLOR_TEXT_BLACK = (15, 23, 42)  # Jet Black / Charcoal
COLOR_TEXT_MUTED = (71, 85, 105)  # Slate Gray Explainer
COLOR_STATEMENT_RED = (220, 38, 38)  # Vibrant Crimson Red
COLOR_RED_BG = (254, 242, 242)  # Soft Red Tint Badge
COLOR_DIVIDER = (226, 232, 240)  # Soft Gray Border


class ViralRVCJGenerator:
    def __init__(self):
        self.font_bold = str(FONT_DIR / "NotoSans-Bold.ttf")
        self.font_regular = str(FONT_DIR / "NotoSans-Regular.ttf")

    def _get_font(self, size: int, bold: bool = True) -> ImageFont.FreeTypeFont:
        return ImageFont.truetype(self.font_bold if bold else self.font_regular, size)

    def _wrap_text(self, text: str, font: ImageFont.FreeTypeFont, max_width: int) -> List[str]:
        words = text.split()
        if not words:
            return [text]
        lines = []
        current = words[0]
        for w in words[1:]:
            test = current + " " + w
            bbox = font.getbbox(test)
            if (bbox[2] - bbox[0]) <= max_width:
                current = test
            else:
                lines.append(current)
                current = w
        lines.append(current)
        return lines

    def _download_and_crop_image(self, url: str, target_w: int, target_h: int) -> Optional[Image.Image]:
        try:
            headers = {"User-Agent": "TrendBharatBot/2.0 (Media Pipeline)"}
            resp = requests.get(url, headers=headers, timeout=15)
            if resp.status_code == 200:
                img = Image.open(io.BytesIO(resp.content)).convert("RGBA")
                img_ratio = img.width / img.height
                target_ratio = target_w / target_h

                if img_ratio > target_ratio:
                    new_h = target_h
                    new_w = int(new_h * img_ratio)
                else:
                    new_w = target_w
                    new_h = int(new_w / img_ratio)

                resized = img.resize((new_w, new_h), Image.Resampling.LANCZOS)
                crop_x = (new_w - target_w) // 2
                crop_y = (new_h - target_h) // 2
                cropped = resized.crop((crop_x, crop_y, crop_x + target_w, crop_y + target_h))

                # Boost contrast and sharpness for press photo quality
                enhancer = ImageEnhance.Contrast(cropped.convert("RGB"))
                return enhancer.enhance(1.10).convert("RGBA")
        except Exception as e:
            print(f"[-] Error loading image from {url}: {e}")
        return None

    def create_single_photo_post(
        self,
        viral_badge: str,
        headline_lead: str,
        red_statement: str,
        context_story: str,
        image_url: str,
        output_path: str,
        handle: str = "@InstaTrend",
    ):
        """Creates single high-res photo post with white card and red statement."""
        canvas = Image.new("RGBA", (CANVAS_WIDTH, CANVAS_HEIGHT), COLOR_BG)
        photo_h = 760

        # Load & place high-definition subject image
        photo = self._download_and_crop_image(image_url, CANVAS_WIDTH, photo_h)
        if photo:
            canvas.paste(photo, (0, 0))
        else:
            draw_fb = ImageDraw.Draw(canvas)
            draw_fb.rectangle([(0, 0), (CANVAS_WIDTH, photo_h)], fill=(241, 245, 249))

        draw = ImageDraw.Draw(canvas)

        # Thin divider below image
        draw.line([(0, photo_h), (CANVAS_WIDTH, photo_h)], fill=(203, 213, 225), width=2)

        # Floating brand watermark
        f_wm = self._get_font(24, bold=True)
        wm_bbox = f_wm.getbbox(handle)
        wm_w = wm_bbox[2] - wm_bbox[0]
        draw.rounded_rectangle(
            [(CANVAS_WIDTH - wm_w - 60, 30), (CANVAS_WIDTH - 25, 76)],
            radius=12,
            fill=(0, 0, 0, 190),
            outline=(255, 255, 255, 100),
            width=1,
        )
        draw.text((CANVAS_WIDTH - wm_w - 42, 42), handle, font=f_wm, fill=(255, 255, 255))

        # Text Layout
        self._render_text_block(draw, viral_badge, headline_lead, red_statement, context_story, start_y=795)
        canvas.convert("RGB").save(output_path, "JPEG", quality=95)
        print(f"[+] Rendered single-photo post: {output_path}")

    def create_split_photo_post(
        self,
        viral_badge: str,
        headline_lead: str,
        red_statement: str,
        context_story: str,
        left_image_url: str,
        right_image_url: str,
        left_label: str,
        right_label: str,
        output_path: str,
        handle: str = "@InstaTrend",
    ):
        """
        Creates classic RVCJ dual-person split comparison post:
        - Left 50%: Person A (e.g. Sonia Gandhi) with name label
        - Right 50%: Person B (e.g. Pranab Mukherjee) with name label
        - Middle: Crisp vertical white divider rule
        """
        canvas = Image.new("RGBA", (CANVAS_WIDTH, CANVAS_HEIGHT), COLOR_BG)
        photo_h = 760
        half_w = CANVAS_WIDTH // 2  # 540px each

        # Download and crop both portraits
        left_img = self._download_and_crop_image(left_image_url, half_w, photo_h)
        right_img = self._download_and_crop_image(right_image_url, half_w, photo_h)

        if left_img:
            canvas.paste(left_img, (0, 0))
        if right_img:
            canvas.paste(right_img, (half_w, 0))

        draw = ImageDraw.Draw(canvas)

        # Center split divider (clean white vertical line)
        draw.line([(half_w, 0), (half_w, photo_h)], fill=(255, 255, 255), width=4)
        draw.line([(0, photo_h), (CANVAS_WIDTH, photo_h)], fill=(203, 213, 225), width=2)

        # Name badges on bottom of photos
        f_name = self._get_font(24, bold=True)
        # Left Name Badge
        draw.rounded_rectangle(
            [(30, photo_h - 60), (30 + f_name.getbbox(left_label)[2] + 30, photo_h - 20)], radius=8, fill=(0, 0, 0, 190)
        )
        draw.text((45, photo_h - 52), left_label, font=f_name, fill=(255, 255, 255))

        # Right Name Badge
        r_bbox = f_name.getbbox(right_label)
        draw.rounded_rectangle(
            [(half_w + 30, photo_h - 60), (half_w + 30 + r_bbox[2] + 30, photo_h - 20)], radius=8, fill=(0, 0, 0, 190)
        )
        draw.text((half_w + 45, photo_h - 52), right_label, font=f_name, fill=(255, 255, 255))

        # Center "VS" or "&" pill
        f_vs = self._get_font(22, bold=True)
        draw.ellipse(
            [(half_w - 24, photo_h // 2 - 24), (half_w + 24, photo_h // 2 + 24)],
            fill=(220, 38, 38),
            outline=(255, 255, 255),
            width=2,
        )
        draw.text((half_w - 14, photo_h // 2 - 14), "VS", font=f_vs, fill=(255, 255, 255))

        # Top Right Watermark
        draw.rounded_rectangle(
            [(CANVAS_WIDTH - 210, 30), (CANVAS_WIDTH - 25, 76)],
            radius=12,
            fill=(0, 0, 0, 190),
            outline=(255, 255, 255, 100),
            width=1,
        )
        draw.text((CANVAS_WIDTH - 190, 42), handle, font=f_name, fill=(255, 255, 255))

        # Text Layout
        self._render_text_block(draw, viral_badge, headline_lead, red_statement, context_story, start_y=795)
        canvas.convert("RGB").save(output_path, "JPEG", quality=95)
        print(f"[+] Rendered split-photo post: {output_path}")

    def _render_text_block(
        self,
        draw: ImageDraw.Draw,
        badge_text: str,
        lead_text: str,
        red_statement: str,
        context_story: str,
        start_y: int,
    ):
        curr_y = start_y

        # 1. Viral Badge Pill
        f_badge = self._get_font(24, bold=True)
        b_bbox = f_badge.getbbox(badge_text)
        b_w = b_bbox[2] - b_bbox[0]

        draw.rounded_rectangle(
            [(60, curr_y), (60 + b_w + 36, curr_y + 44)],
            radius=10,
            fill=COLOR_RED_BG,
            outline=COLOR_STATEMENT_RED,
            width=1,
        )
        draw.text((78, curr_y + 10), badge_text, font=f_badge, fill=COLOR_STATEMENT_RED)
        curr_y += 66

        # 2. Main Lead Hook in Bold Black
        if lead_text:
            f_lead = self._get_font(44, bold=True)
            lead_lines = self._wrap_text(lead_text, f_lead, max_width=960)
            for l_line in lead_lines[:2]:
                draw.text((60, curr_y), l_line, font=f_lead, fill=COLOR_TEXT_BLACK)
                curr_y += 54
            curr_y += 10

        # 3. Catchy Statement in BOLD RED with Left Accent Callout Bar
        if red_statement:
            f_quote = self._get_font(46, bold=True)
            quote_lines = self._wrap_text(red_statement, f_quote, max_width=910)
            quote_start_y = curr_y

            total_h = len(quote_lines[:3]) * 58
            draw.rounded_rectangle(
                [(60, quote_start_y + 4), (68, quote_start_y + total_h)], radius=4, fill=COLOR_STATEMENT_RED
            )

            for q_line in quote_lines[:3]:
                draw.text((90, curr_y), q_line, font=f_quote, fill=COLOR_STATEMENT_RED)
                curr_y += 58
            curr_y += 20

        # 4. Context Explainer in Dark Charcoal
        if context_story:
            f_story = self._get_font(32, bold=False)
            story_lines = self._wrap_text(context_story, f_story, max_width=960)
            for s_line in story_lines[:3]:
                draw.text((60, curr_y), s_line, font=f_story, fill=COLOR_TEXT_MUTED)
                curr_y += 44

        # 5. Clean White Footer Bar
        foot_y = CANVAS_HEIGHT - 80
        draw.line([(60, foot_y - 20), (CANVAS_WIDTH - 60, foot_y - 20)], fill=COLOR_DIVIDER, width=2)
        f_foot_b = self._get_font(28, bold=True)
        f_foot_r = self._get_font(26, bold=False)
        draw.text((60, foot_y), "Swipe for full story 👉", font=f_foot_b, fill=COLOR_STATEMENT_RED)
        draw.text(
            (CANVAS_WIDTH - 380, foot_y + 2), "Follow @InstaTrend for updates", font=f_foot_r, fill=COLOR_TEXT_MUTED
        )


def run():
    print("Generating High-Reach Viral RVCJ Posts with Accurate Images...")
    gen = ViralRVCJGenerator()

    # Post 1: Classic Split Comparison (Sonia Gandhi vs Pranab Mukherjee)
    # Using high-definition official portraits
    url_sonia = "https://upload.wikimedia.org/wikipedia/commons/7/7c/Sonia_Gandhi_in_2013.jpg"
    url_pranab = "https://upload.wikimedia.org/wikipedia/commons/a/a9/Pranab_Mukherjee_Portrait_%28cropped%29.jpg"

    gen.create_split_photo_post(
        viral_badge="🚨 SHOCKING POLITICAL CLAIM",
        headline_lead="EXPLOSIVE REVELATION IN NEW BOOK SHOCKS CONGRESS CIRCLES!",
        red_statement="“Pranab Mukherjee desperately wanted to become Prime Minister, it shocked me deeply”",
        context_story=(
            "In a sensational disclosure, Sonia Gandhi speaks on the secret 2004 power struggle and leadership choices."
        ),
        left_image_url=url_sonia,
        right_image_url=url_pranab,
        left_label="Sonia Gandhi",
        right_label="Pranab Mukherjee",
        output_path=str(OUTPUT_DIR / "viral_01_sonia_vs_pranab.jpg"),
        handle="@InstaTrend",
    )

    # Post 2: Entertainment / Megastar Post (Rajinikanth & Jailer 2)
    url_rajini = "https://upload.wikimedia.org/wikipedia/commons/d/d2/Rajinikanth_in_2019.jpg"
    gen.create_single_photo_post(
        viral_badge="🔥 INTERNET IN MELTDOWN",
        headline_lead="THALAIVAR IS BACK! OFFICIAL CONFIRMATION SETS SOCIAL MEDIA ON FIRE!",
        red_statement="“Jailer 2 will be 10X darker and more ruthless than Part 1, script is locked!”",
        context_story=(
            "Director Nelson confirms superstar Rajinikanth will begin shooting soon, sending fans into a frenzy."
        ),
        image_url=url_rajini,
        output_path=str(OUTPUT_DIR / "viral_02_rajinikanth_jailer2.jpg"),
        handle="@InstaTrend",
    )

    # Post 3: High-Stakes Cricket Drama (Babar Azam / Pakistan vs Sri Lanka)
    url_babar = "https://upload.wikimedia.org/wikipedia/commons/4/43/Babar_azam_2023.jpg"
    gen.create_single_photo_post(
        viral_badge="🏏 DO OR DIE DRAMA",
        headline_lead="MASSIVE PRESSURE ON BABAR AZAM AS CRUCIAL WTC CLASH BEGINS!",
        red_statement="“One more loss and our World Test Championship final dream is DEAD!”",
        context_story=(
            "With qualification on the line, Pakistan faces a fiery Sri Lankan attack in a high-stakes test clash."
        ),
        image_url=url_babar,
        output_path=str(OUTPUT_DIR / "viral_03_cricket_wtc_drama.jpg"),
        handle="@InstaTrend",
    )


if __name__ == "__main__":
    run()

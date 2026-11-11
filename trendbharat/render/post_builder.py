"""RVCJ-style high-impact Instagram post builder (1080x1350, 4:5 portrait)
Features:
- Pure White background, jet black typography, and vibrant red statement
- Contrast-graded high-definition subject photography
- Left crimson accent callout bar for quotes
"""

import io
import os
from pathlib import Path
from typing import List, Optional

import requests
from PIL import Image, ImageDraw, ImageEnhance, ImageFont

CANVAS_WIDTH = 1080
CANVAS_HEIGHT = 1350  # 4:5 Instagram Portrait Ratio

FONT_DIR = Path("trendbharat/assets/fonts")

COLOR_BG = (255, 255, 255)  # Crisp Pure White
COLOR_TEXT_BLACK = (15, 23, 42)  # Jet Black / Charcoal
COLOR_TEXT_MUTED = (71, 85, 105)  # Slate Gray Explainer
COLOR_STATEMENT_RED = (220, 38, 38)  # Vibrant Crimson Red
COLOR_RED_BG = (254, 242, 242)  # Soft Red Tint Badge
COLOR_DIVIDER = (226, 232, 240)  # Soft Gray Border


class RVCJPostBuilder:
    def __init__(self, font_dir: Path = FONT_DIR):
        self.font_bold = str(font_dir / "NotoSans-Bold.ttf")
        self.font_regular = str(font_dir / "NotoSans-Regular.ttf")
        self.font_devanagari = str(font_dir / "NotoSansDevanagari-Bold.ttf")

    def _get_font(self, text: str, size: int, bold: bool = True) -> ImageFont.FreeTypeFont:
        font_path = self.font_bold if bold else self.font_regular
        if any("\u0900" <= c <= "\u097f" for c in text) and os.path.exists(self.font_devanagari):
            font_path = self.font_devanagari
        return ImageFont.truetype(font_path, size)

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

    def _download_and_crop(self, url: str, target_w: int, target_h: int) -> Optional[Image.Image]:
        try:
            headers = {"User-Agent": "TrendBharatBot/2.0 (Post Builder)"}
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

                enhancer = ImageEnhance.Contrast(cropped.convert("RGB"))
                return enhancer.enhance(1.10).convert("RGBA")
        except Exception:
            pass
        return None

    def render(
        self,
        badge_text: str,
        headline: str,
        red_statement: str,
        context: str,
        image_url: Optional[str],
        output_path: str,
        handle: str = "@InstaTrend",
    ) -> str:
        canvas = Image.new("RGBA", (CANVAS_WIDTH, CANVAS_HEIGHT), COLOR_BG)
        photo_h = 760

        # 1. Place Subject Photo
        photo = self._download_and_crop(image_url, CANVAS_WIDTH, photo_h) if image_url else None
        if photo:
            canvas.paste(photo, (0, 0))
        else:
            draw_fb = ImageDraw.Draw(canvas)
            draw_fb.rectangle([(0, 0), (CANVAS_WIDTH, photo_h)], fill=(241, 245, 249))

        draw = ImageDraw.Draw(canvas)

        # Image bottom divider
        draw.line([(0, photo_h), (CANVAS_WIDTH, photo_h)], fill=(203, 213, 225), width=2)

        # Floating brand watermark
        f_wm = self._get_font(handle, 24, bold=True)
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

        # 2. Text Layout (Starting at y = 800)
        curr_y = 800

        # Category / Hook Badge
        f_badge = self._get_font(badge_text, 24, bold=True)
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

        # Bold Black Headline Lead
        if headline:
            f_head = self._get_font(headline, 42, bold=True)
            head_lines = self._wrap_text(headline, f_head, max_width=960)
            for h_line in head_lines[:2]:
                draw.text((60, curr_y), h_line, font=f_head, fill=COLOR_TEXT_BLACK)
                curr_y += 52
            curr_y += 10

        # Vibrant Red Statement with Vertical Accent Bar
        if red_statement:
            f_stmt = self._get_font(red_statement, 46, bold=True)
            stmt_lines = self._wrap_text(red_statement, f_stmt, max_width=910)
            stmt_start_y = curr_y

            total_h = len(stmt_lines[:3]) * 58
            draw.rounded_rectangle(
                [(60, stmt_start_y + 4), (68, stmt_start_y + total_h)], radius=4, fill=COLOR_STATEMENT_RED
            )

            for s_line in stmt_lines[:3]:
                draw.text((90, curr_y), s_line, font=f_stmt, fill=COLOR_STATEMENT_RED)
                curr_y += 58
            curr_y += 20

        # Context Explainer
        if context:
            f_ctx = self._get_font(context, 32, bold=False)
            ctx_lines = self._wrap_text(context, f_ctx, max_width=960)
            for c_line in ctx_lines[:3]:
                draw.text((60, curr_y), c_line, font=f_ctx, fill=COLOR_TEXT_MUTED)
                curr_y += 44

        # Clean Footer
        foot_y = CANVAS_HEIGHT - 80
        draw.line([(60, foot_y - 20), (CANVAS_WIDTH - 60, foot_y - 20)], fill=COLOR_DIVIDER, width=2)
        f_fb = self._get_font("Swipe", 28, bold=True)
        f_fr = self._get_font("Follow", 26, bold=False)
        draw.text((60, foot_y), "Swipe for full story 👉", font=f_fb, fill=COLOR_STATEMENT_RED)
        draw.text(
            (CANVAS_WIDTH - 380, foot_y + 2), f"Follow {handle} for daily updates", font=f_fr, fill=COLOR_TEXT_MUTED
        )

        canvas.convert("RGB").save(output_path, "JPEG", quality=95)
        return output_path

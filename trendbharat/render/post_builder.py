"""Three-tier news card layout (Top Headline + Center Photo + Bottom Factual Story).
Matches modern viral Instagram news pages (RVCJ, Inshorts, Brut India):
1. Top Section: Clean Category Badge + Catchy Bold Black Headline
2. Middle Section: High-definition subject photo (smart portrait/face framed)
3. Bottom Section:
   - Key Important Takeaway / Statement in Vibrant Red with Accent Bar
   - Original Factual Information & Context in Dark Charcoal Slate
   - Interaction Footer with Swipe Prompt and Verified Brand Handle
"""

import io
import os
from pathlib import Path
from typing import List, Optional

import requests
from PIL import Image, ImageDraw, ImageEnhance, ImageFont

CANVAS_WIDTH = 1080
CANVAS_HEIGHT = 1350  # 4:5 Instagram Portrait Ratio

COLOR_BG = (255, 255, 255)  # Pure White
COLOR_TEXT_BLACK = (15, 23, 42)  # Jet Black
COLOR_TEXT_MUTED = (51, 65, 85)  # Charcoal Slate for Factual Story
COLOR_STATEMENT_RED = (220, 38, 38)  # Vibrant Crimson Red
COLOR_RED_BG = (254, 242, 242)  # Soft Red Tint Badge
COLOR_DIVIDER = (226, 232, 240)  # Soft Slate Border


class RVCJPostBuilder:
    def __init__(self, font_dir: Optional[Path] = None):
        if font_dir is None:
            font_dir = Path(__file__).resolve().parent.parent / "assets" / "fonts"
        self.font_bold = str(font_dir / "NotoSans-Bold.ttf")
        self.font_regular = str(font_dir / "NotoSans-Regular.ttf")
        self.font_devanagari = str(font_dir / "NotoSansDevanagari-Bold.ttf")
        self.font_tamil = str(font_dir / "NotoSansTamil-Bold.ttf")
        self.font_telugu = str(font_dir / "NotoSansTelugu-Bold.ttf")

    def _get_font(self, text: str, size: int, bold: bool = True) -> ImageFont.FreeTypeFont:
        font_path = self.font_bold if bold else self.font_regular
        dev_chars = sum(1 for c in text if "\u0900" <= c <= "\u097f")
        lat_chars = sum(1 for c in text if "a" <= c.lower() <= "z")
        if dev_chars > lat_chars and os.path.exists(self.font_devanagari):
            font_path = self.font_devanagari
        elif any("\u0b80" <= c <= "\u0bff" for c in text) and os.path.exists(self.font_tamil):
            font_path = self.font_tamil
        elif any("\u0c00" <= c <= "\u0c7f" for c in text) and os.path.exists(self.font_telugu):
            font_path = self.font_telugu
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
            headers = {"User-Agent": "InstaTrendDailyBot/2.0 (contact: admin@instatrend.local)"}
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

                # Smart portrait crop: For taller images, crop from top 15% to preserve faces
                if new_h > target_h:
                    crop_y = int((new_h - target_h) * 0.15)
                else:
                    crop_y = (new_h - target_h) // 2

                cropped = resized.crop((crop_x, crop_y, crop_x + target_w, crop_y + target_h))
                enhancer = ImageEnhance.Contrast(cropped.convert("RGB"))
                return enhancer.enhance(1.08).convert("RGBA")
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
        """Renders three-tier viral news post."""
        canvas = Image.new("RGBA", (CANVAS_WIDTH, CANVAS_HEIGHT), COLOR_BG)
        draw = ImageDraw.Draw(canvas)

        # -------------------------------------------------------------
        # 1. TOP SECTION (Above Image): Category Badge + Bold Headline
        # -------------------------------------------------------------
        top_y = 40

        # Category Badge
        f_badge = self._get_font(badge_text, 22, bold=True)
        b_bbox = f_badge.getbbox(badge_text)
        b_w = b_bbox[2] - b_bbox[0]
        draw.rounded_rectangle(
            [(60, top_y), (60 + b_w + 32, top_y + 40)],
            radius=8,
            fill=COLOR_RED_BG,
            outline=COLOR_STATEMENT_RED,
            width=1,
        )
        draw.text((76, top_y + 9), badge_text, font=f_badge, fill=COLOR_STATEMENT_RED)

        # Top-Right Floating Handle
        f_handle = self._get_font(handle, 22, bold=True)
        h_w = f_handle.getbbox(handle)[2] - f_handle.getbbox(handle)[0]
        draw.text((CANVAS_WIDTH - 60 - h_w, top_y + 9), handle, font=f_handle, fill=(100, 116, 139))

        top_y += 58

        # Catchy Headline in Bold Jet Black
        f_head = self._get_font(headline, 42, bold=True)
        head_lines = self._wrap_text(headline, f_head, max_width=960)
        for h_line in head_lines[:3]:
            draw.text((60, top_y), h_line, font=f_head, fill=COLOR_TEXT_BLACK)
            top_y += 54

        # -------------------------------------------------------------
        # 2. MIDDLE SECTION: Center Stage Image (height = 560px)
        # -------------------------------------------------------------
        img_y_start = 265
        img_h = 560

        photo = self._download_and_crop(image_url, CANVAS_WIDTH, img_h) if image_url else None
        if photo:
            canvas.paste(photo, (0, img_y_start))
        else:
            # Subtle neutral placeholder if image download fails
            draw.rectangle([(0, img_y_start), (CANVAS_WIDTH, img_y_start + img_h)], fill=(241, 245, 249))

        draw = ImageDraw.Draw(canvas)
        draw.line([(0, img_y_start), (CANVAS_WIDTH, img_y_start)], fill=COLOR_DIVIDER, width=2)
        draw.line([(0, img_y_start + img_h), (CANVAS_WIDTH, img_y_start + img_h)], fill=COLOR_DIVIDER, width=2)

        # -------------------------------------------------------------
        # 3. BOTTOM SECTION: Red Statement + Factual Story + Footer
        # -------------------------------------------------------------
        bot_y = img_y_start + img_h + 35

        # Key Important Statement / Quote in Vibrant Red with Accent Bar
        if red_statement:
            f_stmt = self._get_font(red_statement, 38, bold=True)
            stmt_lines = self._wrap_text(red_statement, f_stmt, max_width=910)
            total_h = len(stmt_lines[:3]) * 48
            draw.rounded_rectangle([(60, bot_y + 4), (68, bot_y + total_h + 4)], radius=4, fill=COLOR_STATEMENT_RED)

            for s_line in stmt_lines[:3]:
                draw.text((90, bot_y), s_line, font=f_stmt, fill=COLOR_STATEMENT_RED)
                bot_y += 48
            bot_y += 20

        # Original Factual Information & Context
        if context:
            f_fact = self._get_font(context, 30, bold=False)
            fact_lines = self._wrap_text(context, f_fact, max_width=960)
            for f_line in fact_lines[:4]:
                draw.text((60, bot_y), f_line, font=f_fact, fill=COLOR_TEXT_MUTED)
                bot_y += 42

        # Bottom Interaction Footer
        foot_y = CANVAS_HEIGHT - 75
        draw.line([(60, foot_y - 20), (CANVAS_WIDTH - 60, foot_y - 20)], fill=COLOR_DIVIDER, width=2)

        f_foot_b = self._get_font("Swipe", 26, bold=True)
        f_foot_r = self._get_font("Follow", 24, bold=False)

        draw.text((60, foot_y), "Swipe for full official report >>", font=f_foot_b, fill=COLOR_STATEMENT_RED)

        follow_text = f"Follow {handle} for verified news"
        follow_bbox = f_foot_r.getbbox(follow_text)
        follow_w = follow_bbox[2] - follow_bbox[0]
        draw.text((CANVAS_WIDTH - 60 - follow_w, foot_y + 2), follow_text, font=f_foot_r, fill=(148, 163, 184))

        canvas.convert("RGB").save(output_path, "JPEG", quality=95)
        return output_path

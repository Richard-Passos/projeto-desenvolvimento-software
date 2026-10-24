from typing import TypedDict

import pygame

from src.model.text_limits import TextLimits


class VisualLine(TypedDict):
    """A piece of a logical line, as drawn (long lines wrap)."""

    text: str
    log_idx: int
    start_pos: int
    end_pos: int


class TextBox:
    def __init__(
        self,
        width: int = 620,
        height: int = 240,
        x: int = 20,
        y: int | None = None,
        limits: TextLimits | None = None,
    ) -> None:
        self.width = width
        self.height = height
        self.x = x
        self.y = y if y is not None else (600 - height - 20)
        self.limits = TextLimits() if limits is None else limits

        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)
        self.number_column_width = 45
        self.scrollbar_width = 12

        self._init_colors()
        self._init_fonts()

        self._text = ''
        self.cursor_pos = 0
        self.selection_anchor = 0
        self.preferred_column_x = 0
        self.box_active = False
        self.scroll_y: float = 0
        self.dragging_scroll = False
        self._active = False

    @property
    def text(self) -> str:
        return self._text

    @text.setter
    def text(self, value: str) -> None:
        self._text = value
        self.cursor_pos = len(self._text)
        self.selection_anchor = self.cursor_pos
        self.scroll_y = 0

    @property
    def is_generated(self) -> bool:
        return self._active

    def generate_text_area(self) -> None:
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)
        self._text = ''
        self.cursor_pos = 0
        self.selection_anchor = 0
        self.scroll_y = 0
        self.box_active = False
        self._active = True

    def kill(self) -> None:
        self._text = ''
        self.box_active = False
        self._active = False

    def handle_events(self, event: pygame.event.Event) -> None:
        if not self._active:
            return

        visual_lines = self._build_visual_lines()
        line_height = self.font.get_linesize()
        total_height = len(visual_lines) * line_height
        visible_height = self.rect.height - 10

        if event.type == pygame.MOUSEWHEEL and self.box_active:
            self.scroll_y -= event.y * 25
            self.scroll_y = max(
                0, min(self.scroll_y, max(0, total_height - visible_height))
            )

        elif event.type == pygame.MOUSEBUTTONDOWN:
            sb_rect = pygame.Rect(
                self.rect.right - self.scrollbar_width - 4,
                self.rect.y + 4,
                self.scrollbar_width,
                self.rect.height - 8,
            )
            if sb_rect.collidepoint(event.pos) and total_height > visible_height:
                self.dragging_scroll = True
            elif self.rect.collidepoint(event.pos):
                self.box_active = True
                mods = pygame.key.get_mods()
                shift = mods & pygame.KMOD_SHIFT

                self.cursor_pos = self._find_pos_by_click(
                    visual_lines, event.pos[0], event.pos[1]
                )
                if not shift:
                    self.selection_anchor = self.cursor_pos
                self._update_preferred_column(visual_lines)
            else:
                self.box_active = False

        elif event.type == pygame.MOUSEBUTTONUP:
            self.dragging_scroll = False

        elif event.type == pygame.MOUSEMOTION and self.dragging_scroll:
            if total_height > visible_height:
                rel_y = event.pos[1] - (self.rect.y + 4)
                proportion = max(0, min(rel_y / (self.rect.height - 8), 1))
                self.scroll_y = proportion * (total_height - visible_height)

        elif event.type == pygame.KEYDOWN and self.box_active:
            self._process_keyboard(event, visual_lines)

    def render(self, surface: pygame.Surface) -> None:
        if not self._active:
            return

        visual_lines = self._build_visual_lines()
        line_height = self.font.get_linesize()
        total_height = len(visual_lines) * line_height
        visible_height = self.rect.height - 10

        max_scroll = max(0, total_height - visible_height)
        self.scroll_y = max(0, min(self.scroll_y, max_scroll))

        pygame.draw.rect(surface, self.inner_color, self.rect)
        border_color = (
            self.active_box_color if self.box_active else self.inactive_box_color
        )
        pygame.draw.rect(surface, border_color, self.rect, 2)

        divider_x = self.rect.x + self.number_column_width
        pygame.draw.line(
            surface,
            self.divider_color,
            (divider_x, self.rect.y + 2),
            (divider_x, self.rect.bottom - 2),
            1,
        )

        self._render_line_numbers(surface, visual_lines, line_height)
        self._render_text_and_selection(surface, visual_lines, line_height, divider_x)
        self._render_scrollbar(surface, total_height, visible_height)

    def _init_colors(self) -> None:
        self.inner_color = (45, 45, 45)
        self.inactive_box_color = (70, 70, 70)
        self.active_box_color = (255, 255, 255)
        self.text_color = (255, 255, 255)
        self.line_number_color = (120, 120, 120)
        self.selection_color = (65, 105, 225)
        self.divider_color = (60, 60, 60)
        self.scroll_color = (100, 100, 100)
        self.scroll_bg_color = (45, 45, 45)

    def _init_fonts(self) -> None:
        self.font = pygame.font.SysFont('Courier New', 18)
        self.font_num = pygame.font.SysFont('Courier New', 14)

    def _util_width(self) -> int:
        return self.rect.width - self.number_column_width - self.scrollbar_width - 15

    def _build_visual_lines(self) -> list[VisualLine]:
        logical_lines = self._text.split('\n')
        visual_lines: list[VisualLine] = []
        max_w = self._util_width()

        char_global_idx = 0
        for log_idx, logical_line in enumerate(logical_lines):
            if logical_line == '':
                visual_lines.append(
                    {
                        'text': '',
                        'log_idx': log_idx,
                        'start_pos': char_global_idx,
                        'end_pos': char_global_idx,
                    }
                )
                char_global_idx += 1
                continue

            current_line = ''
            block_start = char_global_idx

            for char in logical_line:
                test = current_line + char
                if self.font.size(test)[0] > max_w and current_line != '':
                    visual_lines.append(
                        {
                            'text': current_line,
                            'log_idx': log_idx,
                            'start_pos': block_start,
                            'end_pos': block_start + len(current_line),
                        }
                    )
                    block_start += len(current_line)
                    current_line = char
                else:
                    current_line = test

            visual_lines.append(
                {
                    'text': current_line,
                    'log_idx': log_idx,
                    'start_pos': block_start,
                    'end_pos': block_start + len(current_line),
                }
            )
            char_global_idx += len(logical_line) + 1

        return visual_lines

    def _selection_bounds(self) -> tuple[int, int]:
        return (
            min(self.cursor_pos, self.selection_anchor),
            max(self.cursor_pos, self.selection_anchor),
        )

    def _insert(self, value: str) -> None:
        """Type `value` over the selection, unless the text would pass the limits.

        Past the limits nothing happens (no error): the key is just ignored.
        """
        start, end = self._selection_bounds()
        new_text = self._text[:start] + value + self._text[end:]

        if not self.limits.fits(new_text):
            return

        self._text = new_text
        self.cursor_pos = start + len(value)
        self.selection_anchor = self.cursor_pos

    def _delete_selection(self) -> bool:
        if self.selection_anchor != self.cursor_pos:
            s1, s2 = self._selection_bounds()
            self._text = self._text[:s1] + self._text[s2:]
            self.cursor_pos = s1
            self.selection_anchor = s1
            return True
        return False

    def _find_pos_by_click(
        self, visual_lines: list[VisualLine], clicked_x: int, clicked_y: int
    ) -> int:
        line_h = self.font.get_linesize()
        rel_y = clicked_y - (self.rect.y + 8) + self.scroll_y
        vis_idx = max(0, min(int(rel_y // line_h), len(visual_lines) - 1))
        v_line = visual_lines[vis_idx]

        rel_x = clicked_x - (self.rect.x + self.number_column_width + 8)
        best_pos = v_line['start_pos']
        min_dist = 99999
        for i in range(len(v_line['text']) + 1):
            dist = abs(self.font.size(v_line['text'][:i])[0] - rel_x)
            if dist < min_dist:
                min_dist = dist
                best_pos = v_line['start_pos'] + i
        return best_pos

    def _update_preferred_column(self, visual_lines: list[VisualLine]) -> None:
        for v in visual_lines:
            if v['start_pos'] <= self.cursor_pos <= v['end_pos']:
                self.preferred_column_x = self.font.size(
                    v['text'][: self.cursor_pos - v['start_pos']]
                )[0]
                break

    def _process_keyboard(
        self, event: pygame.event.Event, visual_lines: list[VisualLine]
    ) -> None:
        mods = pygame.key.get_mods()
        shift = bool(mods & pygame.KMOD_SHIFT)

        if mods & pygame.KMOD_CTRL:
            if event.key == pygame.K_a:
                self.selection_anchor = 0
                self.cursor_pos = len(self._text)
            elif event.key == pygame.K_c:
                if self.selection_anchor != self.cursor_pos:
                    s1, s2 = self._selection_bounds()
                    pygame.scrap.put(
                        pygame.SCRAP_TEXT, self._text[s1:s2].encode('utf-8')
                    )
            elif event.key == pygame.K_v:
                try:
                    data = pygame.scrap.get(pygame.SCRAP_TEXT)
                except pygame.error:
                    return

                if data:
                    self._insert(data.decode('utf-8', errors='ignore').rstrip('\x00'))
        else:
            if event.key == pygame.K_BACKSPACE:
                if not self._delete_selection() and self.cursor_pos > 0:
                    self._text = (
                        self._text[: self.cursor_pos - 1]
                        + self._text[self.cursor_pos :]
                    )
                    self.cursor_pos -= 1
                    self.selection_anchor = self.cursor_pos
            elif event.key == pygame.K_DELETE:
                if not self._delete_selection() and self.cursor_pos < len(self._text):
                    self._text = (
                        self._text[: self.cursor_pos]
                        + self._text[self.cursor_pos + 1 :]
                    )
                    self.selection_anchor = self.cursor_pos
            elif event.key == pygame.K_RETURN:
                self._insert('\n')
            elif event.key == pygame.K_LEFT:
                if self.cursor_pos > 0:
                    self.cursor_pos -= 1
                if not shift:
                    self.selection_anchor = self.cursor_pos
                self._update_preferred_column(visual_lines)
            elif event.key == pygame.K_RIGHT:
                if self.cursor_pos < len(self._text):
                    self.cursor_pos += 1
                if not shift:
                    self.selection_anchor = self.cursor_pos
                self._update_preferred_column(visual_lines)
            elif event.key in (pygame.K_UP, pygame.K_DOWN):
                self._move_cursor_vertical(
                    visual_lines, event.key == pygame.K_DOWN, shift
                )
            elif event.unicode:
                self._insert(event.unicode)
                self._update_preferred_column(visual_lines)

    def _move_cursor_vertical(
        self, visual_lines: list[VisualLine], downward: bool, shift: bool
    ) -> None:
        curr_vis_idx = 0
        for idx, v in enumerate(visual_lines):
            if v['start_pos'] <= self.cursor_pos <= v['end_pos']:
                curr_vis_idx = idx
                break
        new_idx = curr_vis_idx + 1 if downward else curr_vis_idx - 1
        if 0 <= new_idx < len(visual_lines):
            target_v = visual_lines[new_idx]
            best_pos = target_v['start_pos']
            min_d = 99999
            for i in range(len(target_v['text']) + 1):
                dist = abs(
                    self.font.size(target_v['text'][:i])[0] - self.preferred_column_x
                )
                if dist < min_d:
                    min_d = dist
                    best_pos = target_v['start_pos'] + i
            self.cursor_pos = best_pos
            if not shift:
                self.selection_anchor = self.cursor_pos

    def _render_line_numbers(
        self,
        surface: pygame.Surface,
        visual_lines: list[VisualLine],
        line_height: int,
    ) -> None:
        clip_nums = pygame.Rect(
            self.rect.x + 2,
            self.rect.y + 2,
            self.number_column_width - 2,
            self.rect.height - 4,
        )
        surface.set_clip(clip_nums)
        last_log = -1
        y_offset = self.rect.y + 8 - self.scroll_y
        for v in visual_lines:
            if v['log_idx'] != last_log:
                if self.rect.y <= y_offset < self.rect.bottom:
                    num_surf = self.font_num.render(
                        str(v['log_idx'] + 1), True, self.line_number_color
                    )
                    surface.blit(num_surf, (self.rect.x + 8, y_offset + 2))
                last_log = v['log_idx']
            y_offset += line_height
        surface.set_clip(None)

    def _render_text_and_selection(
        self,
        surface: pygame.Surface,
        visual_lines: list[VisualLine],
        line_height: int,
        divider_x: int,
    ) -> None:
        clip_text = pygame.Rect(
            divider_x + 2,
            self.rect.y + 2,
            self.rect.width - self.number_column_width - self.scrollbar_width - 4,
            self.rect.height - 4,
        )
        surface.set_clip(clip_text)

        y_offset = self.rect.y + 8 - self.scroll_y
        sel_start = min(self.cursor_pos, self.selection_anchor)
        sel_end = max(self.cursor_pos, self.selection_anchor)

        for v in visual_lines:
            if sel_start < v['end_pos'] and sel_end > v['start_pos']:
                l_ini = max(0, sel_start - v['start_pos'])
                l_fim = min(len(v['text']), sel_end - v['start_pos'])
                x_before = self.font.size(v['text'][:l_ini])[0]
                w_sel = self.font.size(v['text'][l_ini:l_fim])[0]
                pygame.draw.rect(
                    surface,
                    self.selection_color,
                    (divider_x + 8 + x_before, y_offset, w_sel, line_height),
                )

            line_surf = self.font.render(v['text'], True, self.text_color)
            surface.blit(line_surf, (divider_x + 8, y_offset))
            y_offset += line_height

        if (
            self.box_active
            and (pygame.time.get_ticks() // 500) % 2 == 0
            and self.selection_anchor == self.cursor_pos
        ):
            for v in visual_lines:
                if v['start_pos'] <= self.cursor_pos <= v['end_pos']:
                    vis_idx = visual_lines.index(v)
                    cx = (
                        divider_x
                        + 8
                        + self.font.size(v['text'][: self.cursor_pos - v['start_pos']])[
                            0
                        ]
                    )
                    cy = self.rect.y + 8 + (vis_idx * line_height) - self.scroll_y
                    pygame.draw.line(
                        surface,
                        self.text_color,
                        (cx, cy),
                        (cx, cy + line_height - 4),
                        2,
                    )
                    break

        surface.set_clip(None)

    def _render_scrollbar(
        self, surface: pygame.Surface, total_height: int, visible_height: int
    ) -> None:
        if total_height > visible_height:
            sb_x = self.rect.right - self.scrollbar_width - 4
            sb_y = self.rect.y + 4
            sb_w = self.scrollbar_width
            sb_h = self.rect.height - 8

            pygame.draw.rect(surface, self.scroll_bg_color, (sb_x, sb_y, sb_w, sb_h))
            thumb_h = max(20, (visible_height / total_height) * sb_h)
            progress = self.scroll_y / max(1, (total_height - visible_height))
            thumb_y = sb_y + progress * (sb_h - thumb_h)
            pygame.draw.rect(
                surface,
                self.scroll_color,
                (sb_x, thumb_y, sb_w, thumb_h),
                border_radius=4,
            )

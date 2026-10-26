from collections.abc import Callable, Mapping
from functools import partial

import pygame

from view.button_bar import Button, ButtonBar
from view.status_bar import StatusBar
from view.text_box import TextBox

type Action = Callable[[], str]


class AppController:
    """The visual part of the app: the window, the views and the main loop.

    It knows nothing about files, sessions or parsing: what the app does comes
    from outside (the main), as functions that return the message to show:

    - `actions`: one button per entry (label -> function). Clicking it runs
      the function and shows what it returns in the status line.
    - `on_start`: runs once the text box exists (e.g. restore the last text).
      What it returns is shown in the status line.
    - `on_close`: runs when the window is closing, while the text box still
      holds its text (e.g. store it).
    """

    TITLE = 'DesenSoftware'
    WINDOW_SIZE = (660, 600)
    FPS = 60
    BACKGROUND = (30, 30, 30)

    def __init__(
        self,
        text_box: TextBox,
        actions: Mapping[str, Action],
        on_start: Action | None = None,
        on_close: Callable[[], None] | None = None,
    ) -> None:
        self._text_box = text_box
        self._on_start = on_start
        self._on_close = on_close

        self._status = StatusBar(x=text_box.x, y=text_box.y - 30)
        buttons = [
            Button(label, partial(self._run, action))
            for label, action in actions.items()
        ]
        self._buttons = ButtonBar(buttons, x=text_box.x)

    def run(self) -> None:
        """Open the window and keep it until the user closes it."""
        screen = self._open_window()

        try:
            self._text_box.generate_text_area()

            if self._on_start is not None:
                self._status.message = self._on_start()

            self._loop(screen)
        finally:
            self._close()

    def _run(self, action: Action) -> None:
        self._status.message = action()

    def _open_window(self) -> pygame.Surface:
        pygame.init()
        screen = pygame.display.set_mode(self.WINDOW_SIZE)
        pygame.display.set_caption(self.TITLE)
        pygame.scrap.init()  # copy and paste of the text box
        pygame.key.set_repeat(400, 35)  # holding a key keeps typing it
        return screen

    def _loop(self, screen: pygame.Surface) -> None:
        clock = pygame.time.Clock()
        running = True

        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                else:
                    self._text_box.handle_events(event)
                    self._buttons.handle_events(event)

            screen.fill(self.BACKGROUND)
            self._buttons.render(screen)
            self._status.render(screen)
            self._text_box.render(screen)
            pygame.display.flip()
            clock.tick(self.FPS)

    def _close(self) -> None:
        try:
            if self._on_close is not None:
                self._on_close()
        finally:
            self._text_box.kill()
            pygame.quit()
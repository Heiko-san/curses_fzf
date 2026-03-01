import curses
from unittest.mock import MagicMock, patch, call
from curses_fzf import ColorTheme
from curses_fzf.help import _help, _base_window

def test_base_window_renders_correctly():
    mock_stdscr = MagicMock(spec=curses.window)
    mock_stdscr.getmaxyx.return_value = (15, 25)

    with patch('curses.color_pair') as mock_color_pair, \
            patch('curses.textpad') as mock_textpad:

        mock_color_pair.side_effect = lambda x: x   # return color pair ID directly

        result = _base_window(
            mock_stdscr,
            "MY TITLE",
            "My Footer is also very long and should be truncated",
            ColorTheme()
        )
        assert result == (15, 25)
        mock_stdscr.clear.assert_called_once()
        mock_stdscr.getmaxyx.assert_called_once()
        mock_textpad.rectangle.assert_called_once_with(mock_stdscr, 1, 0, 15-2, 25-1)
        mock_stdscr.addstr.assert_has_calls([
            call( 1, 2, " MY TITLE ", 33),
            call(14, 2, "My Footer is also ver", 33),
        ], any_order=True)


def test_help():
    mock_stdscr = MagicMock(spec=curses.window)
    mock_stdscr.getmaxyx.return_value = (21, 40)
    mock_stdscr.getch.return_value = curses.KEY_F1 # simulate pressing F1 to exit help

    with patch('curses.color_pair') as mock_color_pair, \
            patch('curses.textpad') as mock_textpad:

        mock_color_pair.side_effect = lambda x: x   # return color pair ID directly

        _help(mock_stdscr, page_size=5, color_theme=ColorTheme())

        mock_stdscr.clear.assert_called_once()
        mock_stdscr.getmaxyx.assert_called_once()
        mock_textpad.rectangle.assert_called_once_with(mock_stdscr, 1, 0, 21-2, 40-1)
        mock_stdscr.addstr.assert_has_calls([
            call(1, 2, " HELP ", 33),
            call(20, 2, "F1 = close help", 33),
            call(5, 7, "text characters", 37),
        ], any_order=True)

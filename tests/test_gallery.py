from unittest.mock import Mock

import pytest

from inky_frame import gallery
from inky_frame.live import ARTWORKS


@pytest.fixture
def gallery_state(tmp_path, monkeypatch):
    monkeypatch.setattr(gallery, "GALLERY_STATE", tmp_path)
    return tmp_path


def test_selection_wraps_and_persists(gallery_state):
    first, *_, last = ARTWORKS
    gallery.choose(first)
    assert gallery.choose("previous") == last
    assert gallery.choose("next") == first
    assert gallery.choose("random") != first
    assert gallery.choose("home") == gallery.HOME
    assert gallery.selection() == gallery.HOME


def test_refresh_coalesces_presses_without_overlapping_workers(gallery_state, monkeypatch):
    monkeypatch.setattr(gallery, "build_view", lambda snapshot, now: snapshot)
    monkeypatch.setattr(gallery, "render", lambda chosen, view, profile: Mock())
    workers = []

    def start(*args, **kwargs):
        worker = Mock()
        worker.poll.return_value = None
        workers.append(worker)
        return worker

    monkeypatch.setattr(gallery.subprocess, "Popen", start)
    player = gallery.Player()
    ids = list(ARTWORKS)
    player.tick(ids[0], {}, 0, 0)
    player.tick(ids[0], {}, 0, 1)
    player.tick(ids[1], {}, 0, 2)
    player.tick(ids[2], {}, 0, 3)
    player.tick(ids[3], {}, 0, 4)
    assert len(workers) == 1
    workers[0].poll.return_value = 0
    player.tick(ids[3], {}, 0, 35)
    assert player.displayed == ids[0]
    assert len(workers) == 1
    player.tick(ids[3], {}, 0, 41)
    assert len(workers) == 2
    assert player.running_artwork == ids[3]


def test_failed_display_is_retried_without_marking_success(gallery_state, monkeypatch):
    monkeypatch.setattr(gallery, "build_view", lambda snapshot, now: snapshot)
    monkeypatch.setattr(gallery, "render", lambda chosen, view, profile: Mock())
    worker = Mock()
    worker.poll.return_value = 1
    popen = Mock(return_value=worker)
    monkeypatch.setattr(gallery.subprocess, "Popen", popen)
    player = gallery.Player()
    player.tick(gallery.HOME, {}, 0, 0)
    player.tick(gallery.HOME, {}, 0, 1)
    player.tick(gallery.HOME, {}, 0, 2)
    assert player.completed is None
    assert player.displayed is None
    assert player.error
    player.tick(gallery.HOME, {}, 0, 61)
    assert popen.call_count == 1
    player.tick(gallery.HOME, {}, 0, 63)
    assert popen.call_count == 2

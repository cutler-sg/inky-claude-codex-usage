import json
from contextlib import contextmanager
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
    assert gallery.selection_state()["mode"] == "locked"
    assert gallery.choose("next") == first
    assert gallery.selection_state()["mode"] == "locked"
    assert gallery.choose("random") != first
    assert gallery.selection_state()["mode"] == "rotate"
    assert gallery.choose("home") == gallery.HOME
    assert gallery.selection() == gallery.HOME
    assert gallery.selection_state()["mode"] == "locked"


@pytest.fixture
def workers(gallery_state, monkeypatch):
    monkeypatch.setattr(gallery, "build_view", lambda snapshot, now: snapshot)
    monkeypatch.setattr(gallery, "render", lambda chosen, view, profile: Mock())
    workers = []

    def start(*args, **kwargs):
        worker = Mock()
        worker.poll.return_value = None
        workers.append(worker)
        return worker

    monkeypatch.setattr(gallery.subprocess, "Popen", start)
    return workers


def snapshot(number=0):
    return {"collected_at": number}


def test_refresh_coalesces_presses_without_overlapping_workers(workers):
    player = gallery.Player()
    ids = list(ARTWORKS)
    gallery.choose(ids[0])
    player.tick(snapshot(), 0, 0)
    player.tick(snapshot(), 0, 1)
    for number in range(1, 4):
        gallery.choose("next")
        player.tick(snapshot(), 0, number + 1)
    assert len(workers) == 1
    workers[0].poll.return_value = 0
    player.tick(snapshot(), 0, 35)
    assert player.displayed == ids[0]
    assert len(workers) == 1
    player.tick(snapshot(), 0, 41)
    assert len(workers) == 2
    assert player.running_artwork == ids[3]


def test_failed_display_is_retried_without_marking_success_or_rotating(workers):
    player = gallery.Player()
    player.tick(snapshot(), 0, 0)
    player.tick(snapshot(), 0, 1)
    workers[0].poll.return_value = 1
    player.tick(snapshot(), 0, 2)
    assert player.completed is None
    assert player.displayed is None
    assert player.error
    player.tick(snapshot(), 0, 61)
    assert len(workers) == 1
    player.tick(snapshot(), 0, 63)
    assert len(workers) == 2
    assert player.running_artwork == gallery.HOME


def test_legacy_selection_defaults_to_rotation_and_restores_same_update(workers, gallery_state):
    gallery.atomic_json(gallery_state / "selection.json", {"artwork": "05-quota-moth"})
    assert gallery.selection_state()["mode"] == "rotate"
    player = gallery.Player()
    player.tick(snapshot(), 0, 0)
    player.tick(snapshot(), 0, 1)
    assert player.running_artwork == "05-quota-moth"
    workers[0].poll.return_value = 0
    player.tick(snapshot(), 0, 35)
    restored = gallery.Player()
    restored.tick(snapshot(), 0, 100)
    restored.tick(snapshot(), 0, 101)
    assert restored.running_artwork == "05-quota-moth"
    assert gallery.selection_state()["mode"] == "rotate"


def test_rotation_advances_once_per_update_and_coalesces_busy_updates(workers):
    player = gallery.Player()
    player.tick(snapshot(), 0, 0)
    player.tick(snapshot(), 0, 1)
    for tick in range(2, 5):
        player.tick(snapshot(tick), tick, tick)
    assert len(workers) == 1
    assert gallery.selection() == gallery.HOME
    workers[0].poll.return_value = 0
    player.tick(snapshot(4), 4, 35)
    assert len(workers) == 1
    player.tick(snapshot(4), 4, 41)
    assert player.running_artwork == "03-reactor-room"
    assert gallery.selection() == "03-reactor-room"
    workers[1].poll.return_value = 0
    for tick in (76, 82, 100, 600):
        player.tick(snapshot(4), 4, tick)
    assert len(workers) == 2


def test_new_collection_rotates_even_when_view_is_identical(workers, monkeypatch):
    monkeypatch.setattr(gallery, "build_view", lambda snapshot, now: {"unchanged": True})
    player = gallery.Player()
    player.tick(snapshot(), 0, 0)
    player.tick(snapshot(), 0, 1)
    workers[0].poll.return_value = 0
    player.tick(snapshot(), 0, 35)
    player.tick(snapshot(1), 0, 41)
    player.tick(snapshot(1), 0, 42)
    assert player.running_artwork == "03-reactor-room"


def test_freshness_transition_rotates_without_new_collection(workers, monkeypatch):
    monkeypatch.setattr(gallery, "build_view", lambda snapshot, now: {"stale": now >= 1200})
    player = gallery.Player()
    player.tick(snapshot(), 0, 0)
    player.tick(snapshot(), 0, 1)
    workers[0].poll.return_value = 0
    player.tick(snapshot(), 0, 35)
    player.tick(snapshot(), 1200, 1200)
    player.tick(snapshot(), 1201, 1201)
    assert player.running_artwork == "03-reactor-room"


def test_lock_persists_across_updates_and_restart_then_random_resumes(workers, monkeypatch):
    gallery.choose("next")
    assert gallery.selection() == "03-reactor-room"
    player = gallery.Player()
    player.tick(snapshot(), 0, 0)
    player.tick(snapshot(), 0, 1)
    workers[0].poll.return_value = 0
    player.tick(snapshot(), 0, 35)
    player.tick(snapshot(1), 1, 41)
    player.tick(snapshot(1), 1, 42)
    assert player.running_artwork == "03-reactor-room"
    workers[1].poll.return_value = 0
    player.tick(snapshot(1), 1, 80)
    restored = gallery.Player()
    restored.tick(snapshot(2), 2, 100)
    restored.tick(snapshot(2), 2, 101)
    assert restored.running_artwork == "03-reactor-room"
    workers[2].poll.return_value = 0
    restored.tick(snapshot(2), 2, 136)
    monkeypatch.setattr(gallery.random, "choice", lambda choices: "06-cosmic-pinball")
    gallery.choose("random")
    restored.tick(snapshot(3), 3, 141)
    restored.tick(snapshot(3), 3, 142)
    assert restored.running_artwork == "06-cosmic-pinball"
    workers[3].poll.return_value = 0
    restored.tick(snapshot(3), 3, 177)
    restored.tick(snapshot(4), 4, 182)
    restored.tick(snapshot(4), 4, 183)
    assert restored.running_artwork == "01-pop-comic"


def test_manual_lock_wins_over_pending_auto_advance(workers):
    player = gallery.Player()
    player.tick(snapshot(), 0, 0)
    player.tick(snapshot(), 0, 1)
    player.tick(snapshot(1), 1, 2)
    gallery.choose("previous")
    player.tick(snapshot(1), 1, 3)
    workers[0].poll.return_value = 0
    player.tick(snapshot(1), 1, 35)
    player.tick(snapshot(1), 1, 41)
    assert player.running_artwork == "01-pop-comic"
    assert gallery.selection_state()["mode"] == "locked"


def test_mode_only_change_updates_status_without_another_refresh(workers, gallery_state):
    player = gallery.Player()
    player.tick(snapshot(), 0, 0)
    player.tick(snapshot(), 0, 1)
    workers[0].poll.return_value = 0
    player.tick(snapshot(), 0, 35)
    gallery.choose("home")
    player.tick(snapshot(), 0, 50)
    assert json.loads((gallery_state / "status.json").read_text())["mode"] == "locked"
    assert len(workers) == 1


def test_resuming_already_displayed_artwork_rotates_on_next_update(workers, monkeypatch):
    player = gallery.Player()
    player.tick(snapshot(), 0, 0)
    player.tick(snapshot(), 0, 1)
    workers[0].poll.return_value = 0
    player.tick(snapshot(), 0, 35)
    gallery.choose("next")
    monkeypatch.setattr(gallery.random, "choice", lambda choices: gallery.HOME)
    gallery.choose("random")
    player.tick(snapshot(), 0, 40)
    assert len(workers) == 1
    player.tick(snapshot(1), 1, 60)
    player.tick(snapshot(1), 1, 61)
    assert player.running_artwork == "03-reactor-room"


def test_concurrent_selection_is_not_overwritten_at_refresh_start(
    workers, monkeypatch, gallery_state
):
    player = gallery.Player()
    player.tick(snapshot(), 0, 0)
    original = gallery.display_cli.display_lock

    @contextmanager
    def race(directory):
        gallery.atomic_json(
            gallery_state / "selection.json", {"artwork": "05-quota-moth", "mode": "locked"}
        )
        with original(directory):
            yield

    monkeypatch.setattr(gallery.display_cli, "display_lock", race)
    player.tick(snapshot(), 0, 1)
    assert not workers
    assert gallery.selection() == "05-quota-moth"


@pytest.mark.parametrize(
    "data",
    [
        [],
        {},
        {"artwork": gallery.HOME, "mode": "invalid"},
        {"artwork": gallery.HOME, "refresh_key": "invalid"},
    ],
)
def test_invalid_selection_reports_an_actionable_error(gallery_state, data):
    gallery.atomic_json(gallery_state / "selection.json", data)
    with pytest.raises(ValueError, match="selection|mode|refresh"):
        gallery.selection_state()

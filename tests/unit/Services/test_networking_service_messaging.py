import asyncio
import json

import pytest

from services.networking_service import NetworkingService


@pytest.fixture
def networking_service():
    service = NetworkingService(port=6000, peer_addresses=[])
    yield service
    service.stop()


def test_split_message_with_topic(networking_service):
    topic, payload = networking_service._split_message("topic {\"value\": 1}")
    assert topic == "topic"
    assert payload == {"value": 1}


def test_split_message_without_topic(networking_service):
    topic, payload = networking_service._split_message("{\"value\": 2}")
    assert topic == ""
    assert payload == {"value": 2}


def test_dispatch_message_invokes_handler(networking_service):
    result = {}

    def handler(payload, topic):
        result["payload"] = payload
        result["topic"] = topic

    networking_service.register_handler("foo", handler)
    networking_service._dispatch_message("foo", {"a": 1})

    assert result == {"payload": {"a": 1}, "topic": "foo"}


def test_broadcast_json_wraps_broadcast(networking_service, monkeypatch):
    sent = {}

    def fake_broadcast(message: str, topic: str = ""):
        sent["message"] = message
        sent["topic"] = topic

    monkeypatch.setattr(networking_service, "broadcast", fake_broadcast)

    networking_service._broadcast_json("bar", {"b": 2})

    assert sent["topic"] == "bar"
    assert json.loads(sent["message"]) == {"b": 2}


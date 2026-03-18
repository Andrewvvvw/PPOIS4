from minesweeper.protocol import arbitrate_winner, decode_buffer, encode_message


def test_protocol_roundtrip() -> None:
    msg = {"type": "state_update", "score": 123, "time_left": 77}
    payload = encode_message(msg)
    messages, tail = decode_buffer(payload)
    assert tail == b""
    assert messages == [msg]


def test_protocol_partial_buffer() -> None:
    full = encode_message({"type": "hello", "name": "A"}) + b'{"type":"hello","name":"B"'
    messages, tail = decode_buffer(full)
    assert len(messages) == 1
    assert messages[0]["name"] == "A"
    assert tail == b'{"type":"hello","name":"B"'


def test_arbitration_hybrid_rules() -> None:
    host = {"status": "win", "completion_time": 70.2, "score": 1200}
    client = {"status": "win", "completion_time": 70.2, "score": 1250}
    result = arbitrate_winner(host, client, "Host", "Client")
    assert result["winner"] == "Client"
    assert result["reason"] == "score_tiebreak"


def test_arbitration_only_one_clears() -> None:
    host = {"status": "loss", "completion_time": None, "score": 500}
    client = {"status": "win", "completion_time": 120.0, "score": 900}
    result = arbitrate_winner(host, client, "Host", "Client")
    assert result["winner"] == "Client"
    assert result["reason"] == "only_clear"


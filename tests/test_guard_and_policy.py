import pytest

from mailroom.errors import MailroomError
from mailroom.guard import guard_decision
from mailroom.policy import recipient_allowed
from mailroom.send import require_localhost


def test_a_gmail_recipient_is_blocked():
    payload = {"tool_name": "send-email", "tool_input": {"to": "sara.ali@gmail.com"}}
    code, message = guard_decision(payload)
    assert code == 2
    assert "sara.ali@gmail.com" in message


def test_a_practice_recipient_is_allowed():
    payload = {"tool_name": "send-email", "tool_input": {"to": "delivered@resend.dev"}}
    assert guard_decision(payload)[0] == 0


def test_other_tools_are_not_guarded():
    assert guard_decision({"tool_name": "write-file", "tool_input": {}})[0] == 0


def test_batch_sends_check_cc_and_bcc_too():
    payload = {"tool_name": "send-batch-emails", "tool_input": {"to": ["a@example.com"], "bcc": ["x@gmail.com"]}}
    assert guard_decision(payload)[0] == 2


@pytest.mark.parametrize(("address", "allowed"), [
    ("ada@example.com", True),
    ("delivered@resend.dev", True),
    ("sara.ali@gmail.com", False),
    ("", False),
])
def test_recipient_rule(address, allowed):
    assert recipient_allowed(address) is allowed


def test_sending_refuses_a_non_local_server():
    with pytest.raises(MailroomError):
        require_localhost("https://api.resend.com")
    require_localhost("http://localhost:4000")

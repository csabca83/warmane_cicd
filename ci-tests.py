from independent_functions.googleauthenticator import get_totp_token
from independent_functions.get_proxies import get_proxies
from independent_functions.human_like_mouse_move import human_like_mouse_move
from independent_functions.log import log
from independent_functions.wait_between import wait_between
import os

RANDOM_MFA = os.environ.get("RANDOM_MFA")


# testing MFA creation
def test_get_totp_token():
    assert get_totp_token(RANDOM_MFA)


def test_get_proxies():
    assert get_proxies()


def test_human_like_mouse_move():

    class Action_testing:

        def move_to_element(startElement):
            print(f"[SUCCESS] Test move: {startElement}")

        def perform():
            print("[SUCCESS] Test Perform call")

        def move_by_offset(mouse_x, mouse_y):
            print("[SUCCESS] Moved by offset:"
                  " on the following position"
                  f"{mouse_x, mouse_y}")

    audioBtn = "Im_a_random_element"

    assert human_like_mouse_move(Action_testing, audioBtn)


def test_log():
    assert log("[SUCCESS] Test")


def test_wait_between():
    assert wait_between(1, 3)

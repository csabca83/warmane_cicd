from googleauthenticator import get_totp_token

RANDOM_MFA = "NQYVIS2VNU7GKTKU"


def test_get_totp_token():
    assert get_totp_token(RANDOM_MFA)

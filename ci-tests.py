from googleauthenticator import get_totp_token

RANDOM_MFA = "NQYVIS2VNU7GKTKU"


# test for travis ci
def test_key():
    get_totp_token(RANDOM_MFA)
    assert True

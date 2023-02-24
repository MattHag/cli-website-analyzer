import pytest

from website_checker.check.cookies_data import cookie_database

COOKIE_CSV_EXAMPLE = [
    (
        "ID,Platform,Category,Cookie / Data Key name,Domain,Description,Retention period,Data Controller,User Privacy &"
        " GDPR Rights Portals,Wildcard match"
    ),
    (
        "256c1410-d881-11e9-8a34-2a2ae2dbcce4,Cookiebot,Functional,CookieConsentBulkTicket,cookiebot.com (3rd"
        " party),Enables sharing cookie preferences across domains / websites,1"
        " year,Cookiebot,https://www.cookiebot.com/en/cookie-declaration/,0"
    ),
    (
        "2caa7a78-e93f-49ca-8fe6-1aaafae1efaa,Google Analytics,Analytics,_gat_gtag_,google-analytics.com (3rd party) or"
        " advertiser's website domain,Used to set and get tracking data,1"
        " hour,Google,https://privacy.google.com/take-control.html,1"
    ),
    (
        "d7496a0e-7f4b-4e20-b288-9d5e4852fa79,Google Analytics,Analytics,_gat_,google-analytics.com (3rd party) or "
        "advertiser's website domain (1st party),ID used to identify users,2 years,Google,"
        "https://privacy.google.com/take-control.html,1"
    ),
    (
        "256c1550-d881-11e9-8a34-2a2ae2dbcce4,Cookiebot,Functional,userlang,cookiebot.com (3rd party),Saves language"
        " preferences of user for a website,1 year,Cookiebot,https://www.cookiebot.com/en/cookie-declaration/,1"
    ),
    (
        "256c1eba-d881-11e9-8a34-2a2ae2dbcce4,Google Analytics,Analytics,AMP_TOKEN,google-analytics.com (3rd party) or"
        " advertiser's website domain (1st party),\"Contains a token code that is used to read out a Client ID from the"
        " AMP Client ID Service. By matching this ID with that of Google Analytics, users can be matched when switching"
        " between AMP content and non-AMP content.\""
    ),
]


@pytest.fixture
def database_csv(tmp_path):
    tmp_file = tmp_path / "cookie_database.csv"
    with open(tmp_file, "w") as f:
        f.write("\n".join(COOKIE_CSV_EXAMPLE))

    yield tmp_file


def test_load_cookie_database(database_csv):
    with cookie_database.CookieDatabase(database_csv) as cookie_db:
        res = cookie_db.data

    assert type(res) == dict
    assert len(res) == len(COOKIE_CSV_EXAMPLE) - 1


def test_search_cookie_database(database_csv):
    cookie_name = "CookieConsentBulkTicket"
    with cookie_database.CookieDatabase(database_csv) as cookie_db:
        res = cookie_db.search(cookie_name)

    assert type(res) == dict
    assert res["cookie_name"] == cookie_name
    assert res["platform"] == "Cookiebot"
    assert res["category"] == "Functional"


def test_search_invalid(database_csv):
    cookie_name = "invalid_name"
    with cookie_database.CookieDatabase(database_csv) as cookie_db:
        with pytest.raises(KeyError):
            cookie_db.search(cookie_name)


@pytest.mark.parametrize(
    "cookie_name,identifier",
    [
        ("_gat_gtag_UA_1234567_1", "2caa7a78-e93f-49ca-8fe6-1aaafae1efaa"),
        ("_gat_1234", "d7496a0e-7f4b-4e20-b288-9d5e4852fa79"),
    ],
)
def test_search_with_wildcard(cookie_name, identifier, database_csv):
    with cookie_database.CookieDatabase(database_csv) as cookie_db:
        res = cookie_db.search(cookie_name)

    assert type(res) == dict
    assert res["cookie_name"] == cookie_name
    assert res["id"] == identifier
    assert res["platform"] == "Google Analytics"


def test_search_invalid_exact_wildcard_match(database_csv):
    cookie_name = "_gat_"
    with cookie_database.CookieDatabase(database_csv) as cookie_db:
        with pytest.raises(KeyError):
            cookie_db.search(cookie_name)

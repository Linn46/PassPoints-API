from pathlib import Path


HOME_HTML = Path(__file__).resolve().parents[2] / "frontend" / "views" / "home.html"
ACCOUNT_HTML = Path(__file__).resolve().parents[2] / "frontend" / "views" / "account.html"
APP_JS = Path(__file__).resolve().parents[2] / "frontend" / "js" / "app.js"
AUTH_JS = Path(__file__).resolve().parents[2] / "frontend" / "js" / "auth.js"


def test_home_education_articles_are_i18n_ready() -> None:
    html = HOME_HTML.read_text(encoding="utf-8")

    assert 'data-i18n="homeConceptTitle"' in html
    assert 'data-i18n="homeConceptText"' in html
    assert 'data-i18n="homeSequenceTitle"' in html
    assert 'data-i18n="homeSequenceText"' in html
    assert 'data-i18n="homeAnalysisTitle"' in html
    assert 'data-i18n="homeAnalysisText"' in html


def test_logged_user_name_is_preserved_on_language_switch() -> None:
    account_html = ACCOUNT_HTML.read_text(encoding="utf-8")
    auth_js = AUTH_JS.read_text(encoding="utf-8")
    app_js = APP_JS.read_text(encoding="utf-8")

    trigger_segment = account_html.split('<strong id="account-trigger-name"', 1)[1]
    trigger_name_only = trigger_segment.split('><small', 1)[0]

    assert 'id="account-trigger-name"' in account_html
    assert 'data-i18n' not in trigger_name_only
    assert 'window.updateAccountUser(window.currentUserState.user);' in auth_js
    assert 'window.updateAccountUser(current.user);' in app_js

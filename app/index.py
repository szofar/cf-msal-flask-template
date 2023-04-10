"""Landing page for the app"""

import msal
from datetime import date
from flask import Flask, render_template, request, make_response, session, redirect, url_for
from flask_session import Session
from db import OpenMongoClientConnection, update_visits
from settings import Settings
from werkzeug.middleware.proxy_fix import ProxyFix


app = Flask(__name__)
app.config.from_object(Settings)
app.secret_key = Settings.SECRET_KEY
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)
Session(app)


def custom_response(to_render):
    """You can customize the response here"""
    response = make_response(to_render)
    return response


def _load_cache():
    cache = msal.SerializableTokenCache()
    if session.get("token_cache"):
        cache.deserialize(session["token_cache"])
    return cache


def _save_cache(cache):
    if cache.has_state_changed:
        session["token_cache"] = cache.serialize()


def _build_msal_app(cache=None, authority=None):
    return msal.ConfidentialClientApplication(
        Settings.CLIENT_ID, authority=authority or Settings.AUTHORITY,
        client_credential=Settings.CLIENT_SECRET, token_cache=cache)


def _build_auth_code_flow(authority=None, scopes=None):
    return _build_msal_app(authority=authority).initiate_auth_code_flow(
        scopes or [],
        redirect_uri=url_for("authorized", _external=True))


def _get_token_from_cache(scope=None):
    cache = _load_cache()  # this web app maintains one cache per session
    cca = _build_msal_app(cache=cache)
    accounts = cca.get_accounts()
    if accounts:  # so all account(s) belong to the current signed-in user
        result = cca.acquire_token_silent(scope, account=accounts[0])
        _save_cache(cache)
        return result


@app.route(Settings.REDIRECT_PATH)  # its absolute URL must match your app's redirect_uri set in AAD
def authorized():
    try:
        cache = _load_cache()
        result = _build_msal_app(cache=cache).acquire_token_by_auth_code_flow(
            session.get("flow", {}), request.args)
        if "error" in result or "MyApp.ReadAccess" not in result.get("id_token_claims", {}).get("roles", {}):
            return redirect(url_for("unauthorized"))
        session["user"] = result.get("id_token_claims")
        _save_cache(cache)
    except ValueError:  # usually caused by CSRF
        pass  # simply ignore them

    return redirect(url_for("dashboard"))


@app.route("/authentication-error")
def unauthorized():
    return custom_response(render_template("auth_error.html"))


@app.route("/logout")
def logout():
    session.clear()
    return redirect(  # also logout from your tenant's web session
        Settings.AUTHORITY + "/oauth2/v2.0/logout" +
        "?post_logout_redirect_uri=" + url_for("dashboard", _external=True))


@app.errorhandler(404)
def not_found(e):
    return render_template("404.html")


@app.route("/", methods=["GET"])
def dashboard():
    """Displays the main dashboard page, optionally using a request query to specify a product_step for initial load"""

    if not session.get("user"):
        session["flow"] = _build_auth_code_flow(scopes=Settings.SCOPE)
        return redirect(session["flow"]["auth_uri"])

    with OpenMongoClientConnection(Settings.DB_CONNECTION_STRING) as client:
        db = client[Settings.DB_NAME]
        dashboard_visits = update_visits(db)

    footer_html = render_template(
        "footer.html",
        fixed_bottom="",
        text_color="black",
        copyright_year=date.today().year,
        page_visits=dashboard_visits)

    to_render = render_template(
        "index.html",
        footer=footer_html)

    return custom_response(to_render)

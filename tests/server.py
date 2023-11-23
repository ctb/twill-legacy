#!/usr/bin/env python3

"""Quixote test app for twill."""

import os
from base64 import decodebytes
from time import sleep
from typing import Optional

from quixote import (  # type: ignore[import-untyped]
    get_path,
    get_request,
    get_response,
    get_session,
    get_session_manager,
    redirect,
)
from quixote.directory import (  # type: ignore[import-untyped]
    AccessControlled,
    Directory,
)
from quixote.errors import AccessError  # type: ignore[import-untyped]
from quixote.form import widget  # type: ignore[import-untyped]
from quixote.publish import Publisher  # type: ignore[import-untyped]
from quixote.session import (  # type: ignore[import-untyped]
    Session,
    SessionManager,
)

HOST = "127.0.0.1"
PORT = 8080


class AlwaysSession(Session):
    """Session that always saves."""

    def __init__(self, session_id: str) -> None:
        """Initialize the session."""
        Session.__init__(self, session_id)
        self.visit = 0

    def has_info(self) -> bool:
        """Return true to indicate that it should always save."""
        return True

    is_dirty = has_info


class UnauthorizedError(AccessError):
    """Error used for Basic Authentication.

    The request requires user authentication.
    This subclass of AccessError sends a 401 instead of a 403,
    hinting that the client should try again with authentication.
    (from http://quixote.ca/qx/HttpBasicAuthentication)
    """

    status_code = 401
    title = "Unauthorized"
    description = "You are not authorized to access this resource."

    def __init__(
        self,
        realm: str = "Protected",
        public_msg: Optional[str] = None,
        private_msg: Optional[str] = None,
    ) -> None:
        """Initialize the error."""
        self.realm = realm
        AccessError.__init__(self, public_msg, private_msg)

    def format(self) -> str:  # noqa: A003
        """Format the error."""
        request = get_request()
        request.response.set_header(
            "WWW-Authenticate", f'Basic realm="{self.realm}"'
        )
        return AccessError.format(self)


def create_publisher() -> None:
    """Create a publisher for TwillTest, with session management added on."""
    session_manager = SessionManager(session_class=AlwaysSession)
    return Publisher(
        TwillTest(),
        session_manager=session_manager,
        display_exceptions="plain",
    )


def message(session: AlwaysSession) -> str:
    """Create a message with session information."""
    return f"""\
<html>
<head>
<title>Hello, world!</title>
</head>
<body>
Hello, world!
<p>
These are the twill tests.
<p>
Your session ID is {session.id}; this is visit #{session.visit}.
<p>
You are logged in as "{session.user}".
<p>
<a href="./increment">increment</a> |
<a href="./incrementfail">incrementfail</a>
<p>
<a href="logout">log out</a>
<p>
(<a href="test spaces">test spaces</a> /
<a href="test_spaces">test spaces2</a>)
</body>
</html>
"""


class TwillTest(Directory):
    """The actual test app."""

    _q_exports = (
        "",
        "logout",
        "increment",
        "incrementfail",
        "restricted",
        "login",
        ("test spaces", "test_spaces"),
        "test_spaces",
        "simpleform",
        "getform",
        "upload_file",
        "http_auth",
        "formpostredirect",
        "exit",
        "multisubmitform",
        "exception",
        "plaintext",
        "xml",
        "sleep",
        "testform",
        "testformaction",
        "test_radiobuttons",
        "test_refresh",
        "test_refresh2",
        "test_refresh3",
        "test_refresh4",
        "test_refresh5",
        "test_checkbox",
        "test_simple_checkbox",
        "echo",
        "test_checkboxes",
        "test_global_form",
        "two_forms",
        "broken_form_1",
        "broken_form_2",
        "broken_form_3",
        "broken_form_4",
        "broken_form_5",
        "broken_linktext",
        "exit",
        "display_post",
        "display_environ",
    )

    def __init__(self) -> None:
        """Initialize the application."""
        self.restricted = Restricted()
        self.http_auth = HttpAuthRestricted()

    def exit(self) -> None:  # noqa: A003
        """Exit the application."""
        raise SystemExit

    def test_global_form(self) -> str:
        """Test the global form."""
        return """
<html>
 <head>
  <title>Broken</title>
 </head>
 <body>
  <div>
  <input name="global_form_entry" type="text">
  <input name="global_entry_2" type="text">
  </div>

  <form name="login" method="post">
  <input type=text name=hello>
  <input type=submit>
  </form>

  <form name="login" method="post"
        action="http://iorich.caltech.edu:8080/display_post">
  <input type=text name=hello>
  <input type=submit>
  </form>

 </body>
</html>
"""

    def display_post(self) -> str:
        """Show the form items."""
        return "".join(
            f"k: '''{k}''' : '''{v}'''<p>\n"
            for k, v in get_request().form.items()
        )

    def display_environ(self) -> str:
        """Show the environment variables."""
        return "".join(
            f"k: '''{k}''' : '''{v}'''<p>\n"
            for k, v in get_request().environ.items()
        )

    def _q_index(self) -> str:
        """Show index page."""
        return message(get_session())

    def broken_form_1(self) -> str:
        """Get broken form 1."""
        return """\
<form>
<input type=text name=blah value=thus>
"""

    def broken_form_2(self) -> str:
        """Get broken form 2."""
        return """\
<form>
<table>
<tr><td>
<input name='broken'>
</td>
</form>
</tr>
</form>
"""

    def broken_form_3(self) -> str:
        """Get broken form 3."""
        return """\
<table>
<tr><td>
<input name='broken'>
</td>
</form>
</tr>
</form>
"""

    def broken_form_4(self) -> str:
        """Get broken form 4."""
        return """\
<font>
<INPUT>

<FORM>
<input type="blah">
</form>
"""

    def broken_form_5(self) -> str:
        """Get broken form 5."""
        return """\
<div id="loginform">
   <form method="post" name="loginform" action="ChkLogin">
   <h3>ARINC Direct Login</h3>
   <br/>
   <strong>User ID</strong><br/>
   <input name="username" id="username" type="text" style="width:80%"><br/>
   <strong>Password</strong><br/>
   <input name="password" type="password" style="width:80%"><br/>
   <div id="buttonbar">
   <input value="Login" name="login" class="button" type="submit">
   </div>
   </form>
</div>
"""

    def broken_linktext(self) -> str:
        """Get broken link text."""
        return """
<a href="/">
<span>some text</span>
</a>
"""

    def test_refresh(self) -> str:
        """Test simple refresh."""
        return """\
<meta http-equiv="refresh" content="2; url=./login">
hello, world.
"""

    def test_refresh2(self) -> str:
        """Test refresh with upper case."""
        return """\
    <META HTTP-EQUIV="REFRESH" CONTENT="2; URL=./login">
    hello, world.
    """

    def test_refresh3(self) -> str:
        """Test circular refresh."""
        return """\
    <meta http-equiv="refresh" content="2; url=./test_refresh3">
    hello, world.
    """

    def test_refresh4(self) -> str:
        """Test refresh together with similar meta tags."""
        return """\
<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN">
<html>
<head>
<title>o2.ie</title>
<meta http-equiv="refresh" content="0;URL=/login">
<meta http-equiv="Content-Type" content="text/html; charset=iso-8859-1">
</head>
<body>
</body>
</html>
hello, world.
"""

    def test_refresh5(self) -> str:
        """Check for situation where given URL is quoted."""
        return """\
<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN">
<html>
<head>
<title>o2.ie</title>
<meta http-equiv="refresh" content="0;'URL=/login'">
<meta http-equiv="Content-Type" content="text/html; charset=iso-8859-1">
</head>
<body>
</body>
</html>
hello, world.
"""

    def exception(self) -> None:
        """Raise a server error."""
        raise RuntimeError("500 error -- fail out!")

    def test_spaces(self) -> str:
        """Test spaces."""
        return "success"

    def sleep(self) -> str:
        """Test timeouts."""
        sleep(0.5)
        return "sorry for the delay"

    def increment(self) -> str:
        """Visit session."""
        session = get_session()
        session.visit += 1
        return message(session)

    def incrementfail(self) -> str:
        """Visit session with failure."""
        session = get_session()
        session.visit += 1
        raise RuntimeError(message(session))

    def login(self) -> str:
        """Test login."""
        request = get_request()
        username_widget = widget.StringWidget(name="username", value="")
        submit_widget = widget.SubmitWidget(name="submit", value="submit me")
        submit_widget2 = widget.SubmitWidget(
            name="nosubmit2", value="don't submit"
        )

        if request.form:
            if submit_widget2.parse(request):
                raise RuntimeError("Cannot parse request.")
            username = username_widget.parse(request)
            if username:
                session = get_session()
                session.set_user(username)
                return redirect("./")

        image_submit = """<input type=image name='submit you' src=DNE.gif>"""

        login = username_widget.render()
        s, s2 = submit_widget.render(), submit_widget2.render()
        img = image_submit
        return f"<form method=POST>Log in: {login}<p>{s2}<p>{s}<p>{img}</form>"

    def simpleform(self) -> str:
        """Test non-existing submit button."""
        request = get_request()

        s1 = widget.StringWidget(name="n", value="").parse(request)
        s2 = widget.StringWidget(name="n2", value="").parse(request)

        return (
            f"{s1} {s2} "
            "<form method=POST>"
            "<input type=text name=n><input type=text name=n2>"
            "</form>"
        )

    def getform(self) -> str:
        """Test form with get method."""
        return (
            "<form method=GET><input type=hidden name=n value=v>"
            "<input type=submit value=send></form>"
        )

    def multisubmitform(self) -> str:
        """Test form with multiple submit buttons."""
        request = get_request()

        submit1 = widget.SubmitWidget("sub_a", value="sub_a")
        submit2 = widget.SubmitWidget("sub_b", value="sub_b")

        s = ""
        if request.form:
            used = False
            if submit1.parse(request):
                used = True
                s += "used_sub_a"
            if submit2.parse(request):
                used = True
                s += "used_sub_b"

            if not used:
                raise RuntimeError("Not button was used.")

            # print out the referer, too.
            referer = request.environ.get("HTTP_REFERER")
            if referer:
                s += f"<p>referer: {referer}"

        s1, s2 = submit1.render(), submit2.render()
        return f"<form method=POST>{s} {s1} {s2}</form>"

    def testformaction(self) -> str:
        """Test form actions."""
        request = get_request()
        keys = sorted(k for k in request.form if request.form[k])
        return "==" + " AND ".join(keys) + "=="

    def testform(self) -> str:
        """Test form."""
        request = get_request()

        s = ""
        if not request.form:
            s = "NO FORM"

        if request.form and "selecttest" in request.form:
            values = request.form["selecttest"]
            if isinstance(values, str):
                values = [values]
            values = " AND ".join(values)
            s += f"SELECTTEST: =={values}==<p>"

        if request.form:
            items = []
            for name in ("item", "item_a", "item_b", "item_c"):
                if request.form.get(name):
                    value = request.form[name]
                    items.append(f"{name}={value}")
            values = " AND ".join(items)
            s += f"NAMETEST: =={values}==<p>"

        return f"""\
{s}
<form method=POST id=the_form>
<select name=selecttest multiple>
<option> val
<option value='selvalue1'> value1 </option>
<option value='selvalue2'> value2 </option>
<option value='selvalue3'> value3 </option>
<option value='test.value3'> testme.val </option>
<option value=Test.Value4> testme4.val </option>
</select>

<input type=text name=item>
<input type=text name=item_a>
<input type=text name=item_b>
<input type=text name=item_c>

<input type=text id=some_id>

<input type=submit value=post id=submit_button>
</form>
"""

    def two_forms(self) -> str:
        """Test two forms."""
        request = get_request()

        if request.form:
            form = request.form.get("form")
            item = request.form.get("item")
            s = f"FORM={form} ITEM={item}"
        else:
            s = "NO FORM"

        return f"""\
<h1>Two Forms</h1>
<p>== {s} ==</p>
<form method=POST id=form1>
<input type=text name=item>
<input type=hidden name=form value=1>
<input type=submit value=post>
</form>
<form method=POST id=form2>
<input type=text name=item>
<input type=hidden name=form value=2>
<input type=submit value=post>
</form>
"""

    def test_checkbox(self) -> str:
        """Test single checkbox."""
        request = get_request()

        s = ""
        if request.form and "checkboxtest" in request.form:
            value = request.form["checkboxtest"]
            if not isinstance(value, str):
                value = value[0]

            s += f"CHECKBOXTEST: =={value}==<p>"

        return f"""\
{s}
<form method=POST>

<input type="checkbox" name="checkboxtest" value="True">
<input type="hidden" name="checkboxtest" value="False">

<input type=submit value=post>
</form>
"""

    def test_checkboxes(self) -> str:
        """Test multiple checkboxes."""
        request = get_request()

        s = ""
        if request.form and "checkboxtest" in request.form:
            value = request.form["checkboxtest"]
            if not isinstance(value, str):
                value = ",".join(value)

            s += f"CHECKBOXTEST: =={value}==<p>"

        return f"""\
{s}
<form method=POST>
<input type="checkbox" name="checkboxtest" value="one">
<input type="checkbox" name="checkboxtest" value="two">
<input type="checkbox" name="checkboxtest" value="three">
<input type=submit value=post>
</form>
"""

    def test_simple_checkbox(self) -> str:
        """Test simple checkbox."""
        request = get_request()

        s = ""
        if request.form and "checkboxtest" in request.form:
            value = request.form["checkboxtest"]
            if not isinstance(value, str):
                value = value[0]

            s += f"CHECKBOXTEST: =={value}==<p>"

        return f"""\
{s}
<form method=POST>

<input type="checkbox" name="checkboxtest">

<input type=submit value=post>
</form>
"""

    def test_radiobuttons(self) -> str:
        """Test radio buttons."""
        request = get_request()

        s = ""
        if request.form and "radiobuttontest" in request.form:
            value = request.form["radiobuttontest"]
            if not isinstance(value, str):
                value = ",".join(value)

            s += f"RADIOBUTTONTEST: =={value}==<p>"

        return f"""\
{s}
    <form method=POST>
    <input type="radio" name="radiobuttontest" value="one">
    <input type="radio" name="radiobuttontest" value="two">
    <input type="radio" name="radiobuttontest" value="three">
    <input type=submit value=post>
    </form>
    """

    def formpostredirect(self) -> str:
        """Test redirect after a form POST."""
        request = get_request()

        if not request.form:
            return """\
<form method=POST enctype=multipart/form-data>
<input type=text name=test>
<input type=submit value=submit name=submit>
</form>
"""
        return redirect(get_path(1) + "/")

    def logout(self) -> str:
        """Test logout."""
        get_session_manager().expire_session()
        return redirect(get_path(1) + "/")  # back to index page

    def plaintext(self) -> str:
        """Test plain text response."""
        response = get_response()
        response.set_content_type("text/plain")
        return "hello, world"

    def xml(self) -> str:
        """Test XML response."""
        response = get_response()
        response.set_content_type("text/xml")
        return '<?xml version="1.0" encoding="utf-8" ?><foo>bår</foo>'

    def echo(self) -> str:
        """Show form content."""
        request = get_request()
        if request.form and "q" in request.form:
            return request.form["q"]
        return "<html><body>No Content</body></html>"

    def upload_file(self) -> str:
        """Test file upload."""
        request = get_request()
        if request.form:
            return request.form["upload"].fp.read()
        return """\
<form enctype=multipart/form-data method=POST>
<input type=file name=upload>
<input type=submit value=submit>
</form>"""


class Restricted(AccessControlled, Directory):
    """A directory with restricted access."""

    _q_exports = ("",)

    def _q_access(self) -> None:
        """Check access."""
        session = get_session()
        if not session.user:
            raise AccessError("you must have a username")

    def _q_index(self) -> str:
        """Show index page."""
        return "you made it!"


class HttpAuthRestricted(AccessControlled, Directory):
    """A directory with restricted access using Basic Authentication."""

    _q_exports = ("",)

    def _q_access(self) -> None:
        """Check access."""
        r = get_request()

        login = passwd = None
        ha = r.get_environ("HTTP_AUTHORIZATION", None)
        if ha:
            auth_type, auth_string = ha.split(None, 1)
            if auth_type.lower() == "basic":
                auth_string = decodebytes(auth_string.encode("utf-8"))
                login, passwd = auth_string.split(b":", 1)
                login = login.decode("utf-8")
                passwd = passwd.decode("utf-8")
                if (login, passwd) != ("test", "password"):
                    passwd = None

        if passwd:
            print(f"Successful login as '{login}'")
        elif login:
            print(f"Invalid login attempt as '{login}'")
        else:
            print("Access has been denied")
        print()
        if not passwd:
            raise UnauthorizedError

    def _q_index(self) -> str:
        """Show index page."""
        return "you made it!"


if __name__ == "__main__":
    from quixote.server.simple_server import (  # type: ignore[import-untyped]
        run,
    )

    port = int(os.environ.get("TWILL_TEST_PORT", PORT))
    print(f"starting twill test server on port {port}.")
    try:
        run(create_publisher, host=HOST, port=port)
    except KeyboardInterrupt:
        print("Keyboard interrupt ignored.")

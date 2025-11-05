from app import app
from flask import abort, render_template

@app.route("/forbidden")
def test_forbidden():
    abort(403)

@app.route("/abort404")
def abort404():
    abort(404)
@app.route("/abort500")
def abort500():
    abort(500)

@app.route("/test418")
def test418():
    abort(418)

@app.route("/crash")
def crash():
    raise Exception("boom")  # JSON 500

@app.errorhandler(403)
def forbidden_error(e):
    return render_template('error_page/403.html'), 403

@app.errorhandler(404)
def not_found_error(e):
    return render_template('error_page/404.html'), 404

@app.errorhandler(500)
def internal_error(e):
    return render_template('error_page/500.html'), 500

@app.errorhandler(Exception)
def global_error_handler(e):
    code = getattr(e, 'code', 500)

    if code in (403, 404, 500):
        raise e

    return render_template('error_page/error.html', code=code), code


# @app.errorhandler(403)
# def forbidden_error(e):
#     return jsonify(error="Forbidden", status=403,
#                    message="You are not allowed to access this resource."), 403
#
# @app.errorhandler(404)
# def not_found_error(e):
#     return jsonify(error="Not Found", status=404,
#                    message="The requested resource was not found."), 404
#
# @app.errorhandler(500)
# def internal_error(e):
#     return jsonify(error="Internal Server Error", status=500,
#                    message="Something went wrong on the server."), 500

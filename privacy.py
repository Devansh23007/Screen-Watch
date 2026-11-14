import config


def is_blocked(app, title):
    app, title = (app or "").lower(), (title or "").lower()
    if any(b in app for b in config.BLOCKED_APPS):
        return True
    return any(k in title for k in config.BLOCKED_KEYWORDS)

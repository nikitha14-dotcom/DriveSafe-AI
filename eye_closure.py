"""Shared eye-closure decision for the MediaPipe camera entry points."""


def eyes_closed(ear, blendshapes, ear_threshold=0.21, blink_threshold=0.5):
    """Use the model's per-eye blink scores when available, with EAR as backup.

    Both eyes must indicate closure; a wink must not start the drowsiness timer.
    """
    scores = {category.category_name: category.score for category in blendshapes}
    left = scores.get("eyeBlinkLeft")
    right = scores.get("eyeBlinkRight")
    if left is not None and right is not None:
        return left >= blink_threshold and right >= blink_threshold
    return ear < ear_threshold


def update_drowsiness(closed, started_at, now, duration):
    """Return (start time, alarm state, elapsed seconds); reset on open/no face."""
    if not closed:
        return None, False, 0.0
    if started_at is None:
        started_at = now
    elapsed = now - started_at
    return started_at, elapsed >= duration, elapsed
"""Timing sequence validation."""

from __future__ import annotations

from .errors import ValidationError


class TimingValidator:
    """Validates timing constraints in MML documents.

    Validates:
    - Monotonically increasing timing within tracks
    - Musical time requires tempo and time signature
    - Relative timing requires a previous event
    """

    def __init__(self):
        self.errors: list[ValidationError] = []
        self.last_absolute_time: float | None = None
        self.has_tempo: bool = False
        self.has_time_signature: bool = False

    def validate(self, doc) -> list[ValidationError]:
        """Validate all timing constraints in a document.

        Args:
            doc: MML document with events and metadata

        Returns:
            List of ValidationError objects
        """
        self.errors = []
        self.last_absolute_time = None
        self.has_tempo = False
        self.has_time_signature = False

        # Check frontmatter for tempo and time signature
        if hasattr(doc, "frontmatter") and doc.frontmatter:
            self.has_tempo = "tempo" in doc.frontmatter
            self.has_time_signature = "time_signature" in doc.frontmatter

        # Validate timing for each event
        self._validate_events(doc.events)

        return self.errors

    def _validate_events(self, events: list) -> None:
        """Validate timing for all events in a list.

        Args:
            events: List of events (can be dicts with 'timing' or objects with timing attr)
        """
        # Validate events in document order (do NOT sort)
        # Timing must be monotonically increasing as written in the source
        has_previous_event = False

        for event in events:
            # Skip non-event tokens (like SECTION_HEADER)
            if not isinstance(event, dict | object) or not hasattr(event, "__dict__"):
                if not isinstance(event, dict):
                    continue

            # Get timing from event
            timing = None
            if isinstance(event, dict) and "timing" in event:
                timing = event["timing"]
            elif hasattr(event, "timing"):
                timing = event.timing

            if not timing:
                continue

            # Validate based on timing type
            if timing.type == "musical":
                self._validate_musical_timing(timing)
            elif timing.type == "relative":
                self._validate_relative_timing(timing, has_previous_event)
            elif timing.type == "absolute":
                self._validate_absolute_timing(timing)
            elif timing.type == "simultaneous":
                # Simultaneous timing requires a previous event
                if not has_previous_event:
                    self.errors.append(
                        ValidationError(
                            "Simultaneous timing [@] requires a previous event",
                            line=getattr(timing, "source_line", 0),
                            error_code="E212",
                            suggestion="Simultaneous timing [@] can only appear after another timed event. "
                            "Add an absolute or relative timestamp first (e.g., [00:00.000] or [+100ms]).",
                        )
                    )

            # Mark that we've seen at least one event
            has_previous_event = True

    def _validate_musical_timing(self, timing) -> None:
        """Validate musical time requires tempo and time signature.

        Args:
            timing: Timing object with type='musical'
        """
        if not self.has_tempo:
            self.errors.append(
                ValidationError(
                    "Musical time requires 'tempo' to be defined in frontmatter",
                    line=getattr(timing, "source_line", 0),
                    error_code="E212",
                    suggestion="Add 'tempo: <bpm>' to the YAML frontmatter. Example: tempo: 120",
                )
            )

        if not self.has_time_signature:
            self.errors.append(
                ValidationError(
                    "Musical time requires 'time_signature' to be defined in frontmatter",
                    line=getattr(timing, "source_line", 0),
                    error_code="E212",
                    suggestion="Add 'time_signature: [<numerator>, <denominator>]' to the frontmatter. "
                    "Example: time_signature: [4, 4]",
                )
            )

    def _validate_relative_timing(self, timing, has_previous_event: bool) -> None:
        """Validate relative timing requires a previous event.

        Args:
            timing: Timing object with type='relative'
            has_previous_event: Whether there's a previous event to be relative to
        """
        if not has_previous_event:
            self.errors.append(
                ValidationError(
                    f"Relative timing {timing.raw} requires a previous event",
                    line=getattr(timing, "source_line", 0),
                    error_code="E212",
                    suggestion="Relative timing (like [+100ms] or [+1b]) can only appear after another event. "
                    "Start with an absolute timestamp first (e.g., [00:00.000]).",
                )
            )

    def _validate_absolute_timing(self, timing) -> None:
        """Validate absolute timing is monotonically increasing.

        Args:
            timing: Timing object with type='absolute'
        """
        # timing.value should be in seconds (float)
        current_time = timing.value

        if self.last_absolute_time is not None and current_time < self.last_absolute_time:
            delta = self.last_absolute_time - current_time
            self.errors.append(
                ValidationError(
                    f"Time {self._format_time(current_time)} is before previous event at "
                    f"{self._format_time(self.last_absolute_time)}. "
                    f"Timing must be monotonically increasing",
                    line=getattr(timing, "source_line", 0),
                    error_code="E212",
                    suggestion=f"Events must appear in chronological order. This event is {delta:.3f}s too early. "
                    f"Move it to [{self._format_time(self.last_absolute_time)}] or later.",
                )
            )

        # Update last absolute time
        if self.last_absolute_time is None or current_time > self.last_absolute_time:
            self.last_absolute_time = current_time

    def _format_time(self, seconds: float) -> str:
        """Format seconds as mm:ss.mmm.

        Args:
            seconds: Time in seconds

        Returns:
            Formatted time string
        """
        minutes = int(seconds // 60)
        remaining_seconds = seconds % 60
        return f"{minutes:02d}:{remaining_seconds:06.3f}"

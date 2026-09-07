"""Sourced Jetson knowledge, as plain Python data (no third-party deps).

This package holds the agent's **domain** content — what it knows about NVIDIA
Jetson devices — separate from the CLI that renders it. One module per topic.

Shape of a topic module (deliberately minimal — this is the first topic, not a
repo-wide schema yet; see the ``Sourcing`` note below):

* ``TOPIC`` / ``TITLE`` / ``SUMMARY`` — identity and a one-paragraph answer.
* ``SOURCES`` — ``{source_id: {"title", "url", "kind"}}``.
* ``CLAIMS`` — ordered ``{"id", "statement", "commands", "sources",
  "confidence"}`` records; every ``sources`` entry is a key of ``SOURCES``.
* ``GAPS`` — what is *not* sourced yet, stated plainly rather than papered over.

Sourcing
--------
The mission is a knowledge base where every claim cites its source and gaps are
honest. There is no repo-wide citation schema yet, and this module does not
invent one — it is the smallest shape that lets a first topic carry real
citations and real gaps. Generalising it (a schema, a loader, validation) is
open work; when that lands, this module is the thing it has to fit.
"""

from __future__ import annotations

from jetson.knowledge import boot_mode

TOPICS = {boot_mode.TOPIC: boot_mode}

__all__ = ["TOPICS", "boot_mode"]

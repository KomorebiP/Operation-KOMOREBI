# Outer-tool launch receipt

The container tool call launching the full candidate verifier returned `TransportTimeoutError`. A subsequent process and report inspection showed that the already launched verifier was running and had completed 26 stages. It was not restarted or counted as passed at that point. Later inspection found its completed report and the shell exit receipt zero. All 137 recorded compiler, axiom, replay and control stages completed with their required outcomes and no subprocess timeout.

This is a manually recorded description of the tool-level interruption. The actual accepted execution evidence is `release_run/report.json` and its retained console log. The outer-tool error is not relabeled as a successful tool call.

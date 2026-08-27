# Concepts You Need Before the Labs

A short, plain-language primer. Read this first if any term below is
unfamiliar, then go into the lab itself.

**Race condition.** A bug that only happens when two things run at
almost the same time. Two people submitting the same task at nearly
the same moment can both check "does this task already exist?", both
get "no," and both create one. TaskFlow's Defect #1 is exactly this.

**Idempotency / idempotency key.** A unique tag attached to a request
so the server can recognize "I've already handled this exact request"
and not repeat the side effect if the request arrives again -- which
happens often, since a slow network can make a client retry a request
that actually succeeded the first time.

**Database migration.** Code that changes a database's structure over
time (adding a column, adding a constraint) in a tracked, repeatable
way. Every migration in this project has an `upgrade()` (apply the
change) and a `downgrade()` (undo it). A migration with a broken
`downgrade()` means you can move a database forward but never safely
back.

**Unique constraint.** A rule enforced by the database itself, not
just application code: "no two rows in this column may have the same
value." This matters because an application-level check ("look up
whether this exists before creating it") has a timing gap a database
constraint does not.

**Timeout / retry / circuit breaker.** A timeout says "give up waiting
after N seconds" instead of waiting forever. A retry policy says "if
it fails, try again, up to N times," usually with increasing delay
(backoff). A circuit breaker stops trying entirely for a cooldown
period after enough consecutive failures, protecting a struggling
downstream system.

**Backpressure / rate limiting.** If more work arrives than a system
can safely handle, backpressure means saying "no, not right now"
instead of accepting everything and collapsing. A rate limiter caps
how much work can be sent in a given time window.

**Characterization test.** A test that documents what code *currently*
does, so any future change to that behavior -- intentional or
accidental -- shows up as a failing test. Written when nobody knows
for certain what the code is "supposed to" do, as the safe first step
before changing anything.

**CLAUDE.md / AGENTS.md.** A file an AI coding tool reads
automatically at the start of a session, containing durable facts
about a codebase (build commands, non-negotiable rules, architecture
notes) so they don't need to be retyped every session.

**Skill.** A packaged, reusable procedure an AI coding tool can follow
the same way every time.

---

**A note on why this app looks the way it does:** TaskFlow is built
with zero external dependencies on purpose -- stdlib `http.server` and
`sqlite3` only. Every concept above (a race condition, a missing
timeout, an unsafe migration, a PII-in-logs leak) is a general
software engineering problem, not a Python-specific one. If you know
these concepts, you could find and fix the equivalent bugs in a Java,
Node, or Go codebase using the same reasoning -- only the syntax
changes.

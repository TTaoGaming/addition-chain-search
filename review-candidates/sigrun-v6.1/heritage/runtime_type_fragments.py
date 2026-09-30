# Exact selected declarations from a historical Python reconstruction candidate.
# Dependencies and implementation bodies live in private source; this excerpt is not a runnable standalone module.

@dataclass(frozen=True)
class ActorGenome:
    actor_id: str
    callsign: str
    actor_class: str
    role: str
    protocol: str
    invariants: frozenset[str]
    invariant_bindings: Mapping[str, str]
    semantic_handles: Mapping[str, Mapping[str, str]]
    obligations: frozenset[str]
    obligation_tests: Mapping[str, str]
    front_door: str
    declared_poetry_sha256: str



@dataclass(frozen=True)
class RuntimeAttestation:
    observer_id: str
    observed_at_utc: str
    expires_at_utc: str
    mechanisms: frozenset[str]
    independent: bool

@dataclass(frozen=True)
class RegenerationEvidence:
    history_status: str
    accepted_history_refs: tuple[str, ...]
    scars: tuple[str, ...]
    open_obligations: tuple[str, ...]
    world_observed_at_utc: str | None
    world_expires_at_utc: str | None
    contradictions: tuple[str, ...] = ()

@dataclass(frozen=True)
class RegenerationResult:
    status: str
    actor_id: str
    reasons: tuple[str, ...]
    effect_authority: str = "NONE"



@dataclass(frozen=True)
class AuthorityEnvelope:
    actor_id: str
    workitem_ref: str
    lease_id: str
    fencing_epoch: int
    effect_class: str
    effect_ceiling: str
    params_sha256: str
    operation_key: str
    idempotent: bool
    expires_at_utc: str

@dataclass
class ActorRuntime:
    genome: ActorGenome
    carrier_id: str
    phase: str = "READY"
    authority: AuthorityEnvelope | None = None
    attempted: bool = False
    receipt_ref: str | None = None
    result_digest: str | None = None



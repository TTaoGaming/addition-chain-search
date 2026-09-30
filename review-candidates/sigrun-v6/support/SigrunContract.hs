-- Generated local representation. Native GHC execution has not been tested.
-- No runtime bindings or permissions are created by importing this module.
module SigrunContract where

hive :: [String]
hive = ["Hindsight", "Insight", "Validated Foresight", "Evolution"]

hiveESpelling :: String
hiveESpelling = "EVOLUTION_OPERATOR_CONFIRMED"

prey :: [String]
prey = ["PERCEIVE", "REACT", "EXECUTE", "YIELD"]

yieldObligations :: [String]
yieldObligations = ["DURABLE_HANDOFF", "RELEASE_BOUNDED_CAPABILITY", "STOP"]

data IdentityEvidence = InfrastructureOnly | MissingAccess | ExternalAuthentication
  deriving (Eq, Show)

identityConclusion :: IdentityEvidence -> String
identityConclusion InfrastructureOnly = "UNVERIFIED"
identityConclusion MissingAccess = "DISCONNECTED_OR_UNVERIFIED"
identityConclusion ExternalAuthentication = "CHECK_TRUST_ROOT_AND_SCOPED_AUTHORIZATION"

-- The seed itself does not supply authentication or authorization.
seedGrantsAuthority :: Bool
seedGrantsAuthority = False

behavioralRegeneration :: String
behavioralRegeneration = "NOT_ESTABLISHED"

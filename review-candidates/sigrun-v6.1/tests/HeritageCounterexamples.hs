module Main where
import Gleipnir
main :: IO ()
main = do
  let r = Ratchet (maxBound :: Int)
  print ("ratchet_overflow_counterexample", strengthen r 1 < r)
  print ("identity_instance_only", quineHolds Gleipnir)
  print ("noncontracting_iteration_budget_returns_without_status", fixedPoint (\x y -> abs (x-y)) (\x y -> abs (x-y)) (ChiOp (\_ a -> a+1) (\_ e -> e+1)) (0::Double) (0::Double) 0.01 3)

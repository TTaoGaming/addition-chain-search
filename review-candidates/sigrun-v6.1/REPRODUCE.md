# Native replay

With an existing compatible GHC, from this directory:

```sh
mkdir -p build
ghc -Wall -fforce-recomp -fno-code -outputdir build/core heritage/Gleipnir_heritage.hs
ghc -O0 -main-is Gleipnir.main -outputdir build/run heritage/Gleipnir_heritage.hs -o build/gleipnir
./build/gleipnir
ghc -O0 -outputdir build/counterexamples tests/HeritageCounterexamples.hs heritage/Gleipnir_heritage.hs -o build/counterexamples-run
./build/counterexamples-run
ghc -Wall -fforce-recomp -fno-code -outputdir build/kernel heritage/Grimoire_heritage.hs
ghc -Wall -fforce-recomp -fno-code -outputdir build/card heritage/Sigrun_card_heritage.hs
```

The last two commands are expected to fail on the recorded missing definitions. Preserve the failures. The inherited driver prints sixteen PASS labels, including tautological checks; this is not a sixteen-part proof. The native counterexample output demonstrates Int overflow and noncontracting iteration returning at its budget limit.

The recorded compiler was GHC9.6.6 from the official Debian9.6.6-4 amd64 package. See receipts/GHC_TOOLCHAIN.json for the verified package hash/source and isolated-install method. Use your platform's official package source or GHC installer for a compatible compiler; this packet does not include compiler binaries or alter your machine. The selected code uses base-library facilities. No provider, service or credential is needed for these offline checks.
